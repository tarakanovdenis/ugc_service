import json

from apscheduler.schedulers.background import BlockingScheduler

from settings import (
    MODIFIED_TIME,
    ROW_LIMIT,
    FILE_PATH_TO_ES_SCHEMA,
    MOVIES_INDEX_NAME,
    GENRES_INDEX_NAME,
    PERSONS_INDEX_NAME,
    FILE_PATH,
    SCHEDULER_TIME_INTERVAL
)
from state_storage import JsonFileStorage, State
from extract_data import (
    extract_film_works_from_db,
    extract_genres_from_db,
    extract_persons_from_db
)
from transform_data import (
    transform_film_work_data,
    transform_genre_data,
    transform_person_data
)
from search import Search


if __name__ == '__main__':
    # Создать соединение с ES
    es = Search()

    with open(FILE_PATH_TO_ES_SCHEMA, 'rt') as f:
        settings_mappings_data = json.load(f)
        es_index_settings = settings_mappings_data['settings']
        movies_es_index_mappings = settings_mappings_data['mappings']['movies']
        genres_es_index_mappings = settings_mappings_data['mappings']['genres']
        persons_es_index_mappings = settings_mappings_data['mappings']['persons']

    for index_name, index_mapping in zip(
        [MOVIES_INDEX_NAME, GENRES_INDEX_NAME, PERSONS_INDEX_NAME],
        [movies_es_index_mappings, genres_es_index_mappings, persons_es_index_mappings]
    ):
        # Создать индекс
        es.create_index(
            index_name,
            settings=es_index_settings,
            mappings=index_mapping
        )

        # Получить информацию об индексе
        es.get_index_information(index_name=index_name)

    # Создать планировщик
    scheduler = BlockingScheduler()

    json_storage = JsonFileStorage(file_path=FILE_PATH)
    state = State(json_storage)

    def postgres_to_es():
        # Инициализировать пустой список для хранения данных для выполнения
        # валидации и последующей загрузки в ES
        film_works_to_es = []
        genres_to_es = []
        persons_to_es = []

        # Выгружаем состояние из хранилища
        state_storage = state.get_state()

        # Получить записи БД (film_works[0]) и данные состояния
        # для сохранения в хранилище (film_works[1])
        film_works = extract_film_works_from_db(
            state_storage,
            MODIFIED_TIME,
            ROW_LIMIT
        )

        genres = extract_genres_from_db(
            state_storage,
            MODIFIED_TIME,
            ROW_LIMIT
        )

        persons = extract_persons_from_db(
            state_storage,
            MODIFIED_TIME,
            ROW_LIMIT
        )

        if film_works:
            film_works_to_es = film_works[0]
            film_work_substorage_states = film_works[1]

        # Если имеются выгруженные данные из БД, выполнить валидацию
        # и загрузку в ES
        if film_works_to_es:
            validated_film_works_to_es = transform_film_work_data(film_works_to_es)
            es.insert_documents(
                index_name=MOVIES_INDEX_NAME,
                documents=validated_film_works_to_es
            )
            # Установить состояние в каждом субхранилище
            # for substorage in SUBSTORAGES:
            state.set_state(
                'film_work_data',
                film_work_substorage_states['film_work_data']
            )

        if genres:
            genres_to_es = genres[0]
            genre_substorage_states = genres[1]

        # Если имеются выгруженные данные из БД, выполнить валидацию
        # и загрузку в ES
        if genres_to_es:
            validated_genres_to_es = transform_genre_data(genres_to_es)
            es.insert_documents(
                index_name=GENRES_INDEX_NAME,
                documents=validated_genres_to_es
            )
            # Установить состояние в хранилище
            state.set_state(
                'genre_data', genre_substorage_states['genre_data']
            )

        if persons:
            persons_to_es = persons[0]
            person_substorage_states = persons[1]

        # Если имеются выгруженные данные из БД, выполнить валидацию
        # и загрузку в ES
        if persons_to_es:
            validated_persons_to_es = transform_person_data(persons_to_es)
            es.insert_documents(
                index_name=PERSONS_INDEX_NAME,
                documents=validated_persons_to_es
            )
            # Установить состояние в хранилище
            state.set_state(
                'person_data', person_substorage_states['person_data']
            )

    # Планирование задания
    scheduler.add_job(
        postgres_to_es,
        'interval',
        seconds=SCHEDULER_TIME_INTERVAL
    )

    # Запуск запланированного задания
    scheduler.start()
