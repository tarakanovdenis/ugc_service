import psycopg2
from psycopg2.extras import DictCursor

from settings import DSN, FILE_PATH, FILM_WORKS_SUBSTORAGE, \
    PERSONS_SUBSTORAGE, GENRES_SUBSTORAGE
from state_storage import JsonFileStorage, State


# Определить объекты классов хранилища и класса для работы с состоянием системы
json_storage = JsonFileStorage(file_path=FILE_PATH)
state = State(json_storage)


def get_modified_film_work_ids(connection,
                               state_storage,
                               substorage_name: str,
                               modified_time: str,
                               table_name: str,
                               row_limit: int):
    # Запросы по каждой бизнес-сущности реализуются в отдельной транзакции
    with connection:
        with connection.cursor() as cursor:
            # Проверить наличие состояния в хранилище
            if state_storage:
                state_storage_time = list(state_storage['film_work_data'][substorage_name].keys())[0]

            # Если состояние имеется в хранилище, тогда обновить значение
            # соответствующей переменной _modified_time
            # Иначе выполнить поиск с момента времени `MODIFIED_TIME`
            if state_storage:
                modified_time = state_storage_time

            # Извлечь ограниченное количество записей,
            # обновленных за время `modified_time`
            cursor.execute(f'''
            SELECT id, modified
            FROM content.{table_name}
            WHERE modified > '{modified_time}'
            ORDER BY modified
            LIMIT {row_limit}
            ''')

            # Извлечь найденные записи
            modified_ids = cursor.fetchall()

            if modified_ids:
                # Получить время последней обновленной записи
                modified_time = str(modified_ids[-1]['modified'])

                # Получить id выгруженных записей
                modified_ids = tuple(
                    [id['id'] for id in modified_ids]
                )

                # Установить состояние для бизнес-сущности
                # state.set_state(substorage_name, substorage_state_value)

                if table_name == 'person':
                    cursor.execute(f'''
                    SELECT fw.id, fw.modified
                    FROM content.film_work AS fw
                    LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
                    WHERE pfw.person_id IN {modified_ids}
                    ORDER BY modified
                    LIMIT {row_limit}
                    ''')
                    # Получить id выгруженных записей киноработ
                    modified_ids = tuple(
                        [id['id'] for id in cursor.fetchall()]
                    )

                elif table_name == 'genre':
                    if len(modified_ids) == 1:
                        cursor.execute(
                            f'''
                            SELECT fw.id, fw.modified
                            FROM content.film_work AS fw
                            LEFT JOIN content.genre_film_work AS pfw ON pfw.film_work_id = fw.id
                            WHERE pfw.genre_id = '{modified_ids[0]}'
                            ORDER BY modified
                            LIMIT {row_limit}
                            '''
                        )
                    else:
                        cursor.execute(
                            f'''
                            SELECT fw.id, fw.modified
                            FROM content.film_work AS fw
                            LEFT JOIN content.genre_film_work AS pfw ON pfw.film_work_id = fw.id
                            WHERE pfw.genre_id IN {modified_ids}
                            ORDER BY modified
                            LIMIT {row_limit}
                            '''
                        )
                    # Получить id выгруженных записей киноработ
                    modified_ids = tuple(
                        [id['id'] for id in cursor.fetchall()]
                    )

            # Сохранить время обновления последней выгруженной записи
            # в субхранилище с id выгруженных записей
            substorage_state_value = {
                modified_time: modified_ids
            }

            return modified_ids, substorage_state_value


def extract_film_works_from_db(
    state_storage, modified_time: str, row_limit: int
) -> list[psycopg2.extras.DictRow]:
    '''
    Возвращает набор необработанных записей/данных из базы данных (БД).

        Параметры:
            modified_time (str): время, за которое произошло обновление
            записей в БД
            row_limit (int): количество записей, выгружаемых за один
            запрос в БД

        Возвращаемое значение:
            film_works (list[psycopg2.extras.DictRow]): список записей,
            выгруженных из БД
    '''

    # Установить соединение с БД
    connection = psycopg2.connect(**DSN, cursor_factory=DictCursor)

    # Список для хранения id киноработ, которые необходимо загрузить в Elasticsearch
    film_works_to_elasticsearch = []
    substorage_states = {
        'film_work_data': {
            'film_works': {},
            'persons': {},
            'genres': {},
        }
    }

    # Запросы по каждой бизнес-сущности реализуются в отдельной транзакции
    for substorage_name, table_name in [
        (FILM_WORKS_SUBSTORAGE, 'film_work'),
        (PERSONS_SUBSTORAGE, 'person'),
        (GENRES_SUBSTORAGE, 'genre')
    ]:

        modified_film_work_ids, substorage_states['film_work_data'][substorage_name] = get_modified_film_work_ids(
            connection=connection,
            state_storage=state_storage,
            substorage_name=substorage_name,
            modified_time=modified_time,
            table_name=table_name,
            row_limit=row_limit
        )

        # Добавить id выгруженных записей киноработ в список
        # для загрузки в Elasticsearch
        film_works_to_elasticsearch = film_works_to_elasticsearch + list(modified_film_work_ids)

    with connection:
        with connection.cursor() as cursor:
            # Прежде чем выгрузить недостающие данные, соотвествующие
            # извлеченным id киноработ в необходиом формате для последующей
            # валидации данных, проверить остались ли обновленные записи в БД:
            #     - остались - продолжать выгружать данные
            #     - отсутствуют - вывести сообщение о том, что все обновленные
            #     записи извлечены
            if film_works_to_elasticsearch:
                cursor.execute(f'''
                SELECT
                    fw.id,
                    fw.rating AS imdb_rating,
                    COALESCE(
                        ARRAY_AGG(DISTINCT g.name), ARRAY[]::text[]) AS genre,
                    fw.title,
                    fw.description,
                    COALESCE(
                        ARRAY_AGG(DISTINCT p.full_name) FILTER(WHERE pfw.role = 'director'),
                        ARRAY[]::text[]
                    ) AS directors_names,
                    COALESCE(
                        ARRAY_AGG(DISTINCT p.full_name) FILTER(WHERE pfw.role = 'actor'),
                        ARRAY[]::text[]
                    ) AS actors_names,
                    COALESCE(
                        ARRAY_AGG(DISTINCT p.full_name) FILTER(WHERE pfw.role = 'writer'),
                        ARRAY[]::text[]
                    ) AS writers_names,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )) FILTER(WHERE pfw.role = 'actor'),
                        '[]'
                    ) AS actors,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )) FILTER(WHERE pfw.role = 'writer'),
                        '[]'
                    ) AS writers,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', p.id,
                            'name', p.full_name
                        )) FILTER(WHERE pfw.role = 'director'),
                        '[]'
                    ) AS directors
                FROM content.film_work AS fw
                LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
                LEFT JOIN content.person AS p ON pfw.person_id = p.id
                LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
                LEFT JOIN content.genre AS g ON gfw.genre_id = g.id
                WHERE fw.id IN {tuple(set(film_works_to_elasticsearch))}
                GROUP BY fw.id
                ''')
                # Извлечь найденные записи
                modified_film_works = cursor.fetchall()

                return modified_film_works, substorage_states
            print('Все обновленные данные фильмов выгружены.')

    # Закрыть соединение с БД
    connection.close()


def get_modified_genre_ids(
    connection,
    state_storage,
    modified_time: str,
    row_limit: int
):
    # Запросы по каждой бизнес-сущности реализуются в отдельной транзакции
    with connection:
        with connection.cursor() as cursor:
            # Проверить наличие состояния в хранилище
            if state_storage:
                state_storage_time = list(state_storage['genre_data'][GENRES_SUBSTORAGE].keys())[0]

            # Если состояние имеется в хранилище, тогда обновить значение
            # соответствующей переменной _modified_time
            # Иначе выполнить поиск с момента времени `MODIFIED_TIME`
            if state_storage:
                modified_time = state_storage_time

            # Извлечь ограниченное количество записей,
            # обновленных за время `modified_time`
            cursor.execute(f'''
            SELECT id, modified
            FROM content.genre
            WHERE modified > '{modified_time}'
            ORDER BY modified
            LIMIT {row_limit}
            ''')

            # Извлечь найденные записи
            modified_ids = cursor.fetchall()

            if modified_ids:
                # Получить время последней обновленной записи
                modified_time = str(modified_ids[-1]['modified'])

                # Получить id выгруженных записей
                modified_ids = tuple(
                    [id['id'] for id in modified_ids]
                )

                # Установить состояние для бизнес-сущности
                # state.set_state(substorage_name, substorage_state_value)

            # Сохранить время обновления последней выгруженной записи
            # в субхранилище с id выгруженных записей
            substorage_state_value = {
                modified_time: modified_ids
            }

            return modified_ids, substorage_state_value


def extract_genres_from_db(
    state_storage, modified_time: str, row_limit: int
) -> list[psycopg2.extras.DictRow]:
    '''
    Возвращает набор необработанных записей/данных из базы данных (БД).

        Параметры:
            modified_time (str): время, за которое произошло обновление
            записей в БД
            row_limit (int): количество записей, выгружаемых за один
            запрос в БД

        Возвращаемое значение:
            genres (list[psycopg2.extras.DictRow]): список записей,
            выгруженных из БД
    '''

    # Установить соединение с БД
    connection = psycopg2.connect(**DSN, cursor_factory=DictCursor)

    # Список для хранения id жанров, которые необходимо загрузить в Elasticsearch
    genres_to_elasticsearch = []
    substorage_states = {
        'genre_data': {}
    }

    modified_genre_ids, substorage_states['genre_data'][GENRES_SUBSTORAGE] = get_modified_genre_ids(
        connection=connection,
        state_storage=state_storage,
        modified_time=modified_time,
        row_limit=row_limit
    )

    # Добавить id выгруженных записей жанров в список
    # для загрузки в Elasticsearch
    genres_to_elasticsearch = genres_to_elasticsearch + list(modified_genre_ids)

    with connection:
        with connection.cursor() as cursor:
            # Прежде чем выгрузить недостающие данные, соотвествующие
            # извлеченным id киноработ в необходиом формате для последующей
            # валидации данных, проверить остались ли обновленные записи в БД:
            #     - остались - продолжать выгружать данные
            #     - отсутствуют - вывести сообщение о том, что все обновленные
            #     записи извлечены
            if genres_to_elasticsearch:
                if len(tuple(set(genres_to_elasticsearch))) == 1:
                    cursor.execute(
                        f'''
                        SELECT id, name, description
                        FROM content.genre
                        WHERE id = '{list((set(genres_to_elasticsearch)))[0]}'
                        GROUP BY id
                        '''
                    )
                else:
                    cursor.execute(
                        f'''
                        SELECT id, name, description
                        FROM content.genre
                        WHERE id IN {tuple(set(genres_to_elasticsearch))}
                        GROUP BY id
                        '''
                    )
                # Извлечь найденные записи
                modified_genres = cursor.fetchall()

                return modified_genres, substorage_states

            print('Все обновленные данные жанров выгружены.')

    # Закрыть соединение с БД
    connection.close()


def get_modified_person_ids(
    connection,
    state_storage,
    modified_time: str,
    row_limit: int
):
    # Запросы по каждой бизнес-сущности реализуются в отдельной транзакции
    with connection:
        with connection.cursor() as cursor:
            # Проверить наличие состояния в хранилище
            if state_storage:
                state_storage_time = list(state_storage['person_data'][PERSONS_SUBSTORAGE].keys())[0]

            # Если состояние имеется в хранилище, тогда обновить значение
            # соответствующей переменной _modified_time
            # Иначе выполнить поиск с момента времени `MODIFIED_TIME`
            if state_storage:
                modified_time = state_storage_time

            # Извлечь ограниченное количество записей,
            # обновленных за время `modified_time`
            cursor.execute(f'''
            SELECT id, modified
            FROM content.person
            WHERE modified > '{modified_time}'
            ORDER BY modified
            LIMIT {row_limit}
            ''')

            # Извлечь найденные записи
            modified_ids = cursor.fetchall()

            if modified_ids:
                # Получить время последней обновленной записи
                modified_time = str(modified_ids[-1]['modified'])

                # Получить id выгруженных записей
                modified_ids = tuple(
                    [id['id'] for id in modified_ids]
                )

                # Установить состояние для бизнес-сущности
                # state.set_state(substorage_name, substorage_state_value)

            # Сохранить время обновления последней выгруженной записи
            # в субхранилище с id выгруженных записей
            substorage_state_value = {
                modified_time: modified_ids
            }

            return modified_ids, substorage_state_value


def extract_persons_from_db(
    state_storage, modified_time: str, row_limit: int
) -> list[psycopg2.extras.DictRow]:
    '''
    Возвращает набор необработанных записей/данных из базы данных (БД).

        Параметры:
            modified_time (str): время, за которое произошло обновление
            записей в БД
            row_limit (int): количество записей, выгружаемых за один
            запрос в БД

        Возвращаемое значение:
            persons (list[psycopg2.extras.DictRow]): список записей,
            выгруженных из БД
    '''

    # Установить соединение с БД
    connection = psycopg2.connect(**DSN, cursor_factory=DictCursor)

    # Список для хранения id жанров, которые необходимо загрузить в Elasticsearch
    persons_to_elasticsearch = []
    substorage_states = {
        'person_data': {}
    }

    modified_person_ids, substorage_states['person_data'][PERSONS_SUBSTORAGE] = get_modified_person_ids(
        connection=connection,
        state_storage=state_storage,
        modified_time=modified_time,
        row_limit=row_limit
    )

    # Добавить id выгруженных записей жанров в список
    # для загрузки в Elasticsearch
    persons_to_elasticsearch = persons_to_elasticsearch + list(modified_person_ids)

    with connection:
        with connection.cursor() as cursor:
            # Прежде чем выгрузить недостающие данные, соотвествующие
            # извлеченным id киноработ в необходиом формате для последующей
            # валидации данных, проверить остались ли обновленные записи в БД:
            #     - остались - продолжать выгружать данные
            #     - отсутствуют - вывести сообщение о том, что все обновленные
            #     записи извлечены
            if persons_to_elasticsearch:
                if len(tuple(set(persons_to_elasticsearch))) == 1:
                    cursor.execute(
                        f'''
                        SELECT id, full_name
                        FROM content.person
                        WHERE id = '{list((set(persons_to_elasticsearch)))[0]}'
                        GROUP BY id
                        '''
                    )
                else:
                    cursor.execute(
                        f'''
                        SELECT id, full_name
                        FROM content.person
                        WHERE id IN {tuple(set(persons_to_elasticsearch))}
                        GROUP BY id
                        '''
                    )
                # Извлечь найденные записи
                modified_persons = cursor.fetchall()

                return modified_persons, substorage_states

            print('Все обновленные данные персон выгружены.')

    # Закрыть соединение с БД
    connection.close()
