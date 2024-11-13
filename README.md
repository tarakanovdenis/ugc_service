# User-Generated Content Service

Проект состоит из следующих сервисов:
- **ugc_flask**: в данном сервисе у пользователя есть возможность взаимодействия с видеоплеером на frontend'e. При этом происходит отслеживание и запись действий пользователя (**Kafka** -> **ELT-процесс** -> **Clickhouse**).
Отслеживание кликов пользователей реализовано через взаимодействие на frontend'е с видеоплеером (на основе `https://codewithsaif.com/how-to-create-custom-video-player-using-html-css-javascript-no-plugin-all-parts/`). В директорию `./ugc/static/` добавлены два видео `360.mp4` и `720.mp4` для смены качества при просмотре. В директории проекта в модуле `./producer.py` реализовано подключение к Kafka. В файле `./ugc_flask/static/script.js` добавлены функции: в строке 198 `sendPauseEvent` для отправки события о нажатии на кнопку паузы; в строке 404 `sendFullViewEvent` для отправки сообщения о просмотре фильма;в строке 535 `sendQualityChangeEvent` для отправки события о смене качества. Сообщения отправляются на сервис UGC, запущенном на Flask, на следующие эндпоинты, соответственно: `/api/pause`, `/api/full-view`, `/api/quality-change`. Сообщения записываются в следующие топики:
    -  `tracking.clicks_on_video.pauses` отслеживание нажатия на кнопку паузы
    - `tracking.clicks_on_video.full_views` отслеживание просмотра фильма
    - `tracking.clicks_on_video.quality_changes` отслеживание нажатия на кнопку смены качества
- **ETL-сервис** для переноса данных из Kafka в ClickHouse - сервис `etl_from_kafka_to_clickhouse`. При старте сервиса создается база данных в ClickHouse: `tracking_user_events`. В базе данных создаются следующие
    таблицы:
        1. Отслеживание кликов:
            -`video_quality_change_clicks`
            -`clicks_on_video_pauses`
            -`clicks_on_video_full_views`
        2. Отслеживание просмотра страниц API:
            -`get_films_page_views`
            -`get_film_by_id_page_views`
            -`search_films_by_keyword_page_views`
            -`get_genres_page_views`
            -`get_genre_by_id_page_views`
            -`get_person_by_id_page_views`
            -`search_persons_by_keyword_page_views`
    В `./ugc/etl/queries.py` описаны все необходимые запросы в ClickHouse. Для запуска UI для ClickHouse можно воспользоваться LightHouse (`https://github.com/VKCOM/lighthouse`). Склонировать репозиторий и запустить `index.html`.
- **ugc_fastapi**: сервис представляет собой API, реализующее CRUD для работы с закладками, лайками и рецензиями, и использующее MongoDB в качестве базы данных, выполнено на FastAPI, исходный код представлен в директории `./ugc_fastapi/`.
- **ELK**: подключено логирование запросов через Nginx. Логи сохраняются в json в директорию `./nginx/logs/access-log.json`, директория монтируется в docker-compose и "разделяется" с Filebeat, который загружает записи логов в Elasticsearch.Также отдельно подключено логирование сервиса UGC на FastAPI, через который реализован CRUD с MongoDB. Логи записываются в папку `logs` директории сервиса. C помощью Logstash они выгружаются в Elasticsearch и затем визуализируются в Kibana.
- **notification_service**: сервис для отправки уведомлений, персональных сообщений пользователям посредством получения сообщений из **RabbitMQ**. Также реализована панель администратора сервиса нотификации для отправки пользователям различных сообщений, например, о выходе новых фильмов.
- **auth**: сервис аутентификации и авторизации. Механизм аутентификации и авторизации реализуется через выдачу **JWT-токенов** (access и refresh). В сервисе реализовано взаимодейтсвие с сервисом нотификации через брокер сообщений **RabbitMQ** - пользователь получает персональные сообщения при регистрации и восстановлении пароля, регистрация и аутентификация с использованием **OAuth2** - протокол взаимодействия с Google API, также реализована трассировка запросов в сервис Auth и подключения **Jaeger**. Выполнено **партицирование** таблицы для сохранения истории входов пользователей по типам устройств.
Помимо этого сервис содержит:
    - Через декоратор добавлены проверка прав пользователя для авторизации (в проекте на текущий момент три роли: `public_user`, `admin`, `super_user`) при выполнении запросов по эндпоинтам сервиса.
    - Для создания пользователя можно воспользоватьcя следующей командой, находясь в корневой директории проекта: `python -m src.core.createsuperuser`.
    - Также используется декоратор для ограничения количества запросов к серверу с использованием **Redis**.
    - Для работы **Jaeger** необходимо в файле `./auth/.env` перевести значение переменной `JAEGER_CONFIGURE_TRACER` в значение `True` и запустить скрипт в корневой директории `run_jaeger.sh`. По умолчанию трассировка отключена из-за необходимости наличия в заголовках запросов `X-Request-Id`, из-за чего отсутствует возможность регистрации и аутентификации пользователей через социальные сети.
    - Для доступа к эндпоинту `/auth/login` с других доменов настроен CORS.
    - Для регистрации с использованием OAuth2 необходимо перейти по эндпоинту `/oauth/`.
    - После старта Auth сервиса создаются основные таблицы. При этом необходимо вручную создать партицированные таблицы:
        - `docker compose exec -it auth_db psql -U $(echo $POSTGRES_USER) -d $(echo $POSTGRES_DB) -f create_partition_table_entry_histories.ddl`
- **async_api**: сервис **асинхронного API** для чтения записей используемых данных (кинофильмы, жанры, актеры, режиссеры и сценаристы). Проект реализован посредством взаимодействия следующих компонентов: **PostgreSQL**, **Elasticsearch**, **ETL** для выгрузки данных с **PostgreSQL** и загрузки в **Elasticsearch**, **Redis**, **FastAPI**, **Nginx**. Также написаны тесты (**pytest**) для сервиса Async API. Для получения ответа по эндопоинтам необходимо пройти авторизацию - сперва залогиниться через эндпоинт `auth/login/` сервиса аутентификации и авторизации.
- **etl_from_postgres_to_es**: сервис представляет собой **ETL-процесc** для выгрузки данных из **PostgreSQL**, содержащей данные о фильмах, актерах и жанрах, в **Elasticsearch** в сервисе Async API. Наряду с сервисом реализован скрипт для переноса данных из SQLite3 в PostgreSQL, написаны тесты для проверки корректности переноса.
- **admin_panel**: Проект представляет собой сервис панели администратора для добавления, чтения, редактирования и удаления записей используемых данных (кинофильмы, жанры, актеры, режиссеры и сценаристы).
Также реализовано API для получения списка имеющихся фильмов, задокументировано при помощи **Swagger**.
Сервис запускается с помощью **Docker**, доступ к сервису осуществляется через **Nginx**.
Выполнена внешняя аутентификация - данные учетной записи отправляются на эндпоинт `auth/login/` сервиса аутентификации, откуда извлекаются данные пользователя в виде токена доступа. В нем содержатся основные данные пользователя, в частности, его права - токен декодируется и определяются права пользователя. При наличии прав (роли `admin` и `super_user`) авторизация проходит успешно, и пользователь заходит в сервис. Получив токен доступа, необходимо в интерактивной документации ввести его в поле JWTBearer.

## Перенос данных в базу данных PostgreSQL из SQLite3

Для переноса данных в базу данных PostgreSQL используйте скрипт `load_data.py`, находясь внутри контейнера `etl_from_postgres_to_es`:
- `python sqlite_to_postgres/load_data.py`

Выполнение переноса данных автоматически тестируются c выводом результата проверки.

## Запуск проекта
Проект запускается через docker-compose и состоит из следующих контейнеров:
- django_admin_panel_backend
- swagger
- django_admin_panel_db
- async_api_backend
- kafka + ui + zookeeper
- redis
- elasticsearch
- etl_from_postgres_to_es
- auth_backend
- auth_db
- rabbitmq
- notification_service_backend
- clickhouse
- etl_from_kafka_to_clickhouse
- backend_for_ugc_fastapi
- mongodb
- elasticsearch_elk
- logstash
- kibana
- filebeat
- backend_for_notification_service
- backend_for_notification_service_admin_panel
- nginx
- jaeger (optional)
- pgadmin (optional)

Для **запуска проекта** необходимо выполнить следующее:
- **применить схему и создать таблицы** в контейнере базы данных PostgreSQL - `django_admin_panel_db`:
    - `docker compose exec -it postgres_db psql -U $(echo $POSTGRES_USER) -d $(echo $POSTGRES_DB) -f movies_database.dll`
- **перенести данные** из **SQLite** в **PostgreSQL** и проверить корректность переноса данных (реализован скрипт и написаны соответствующие тесты для переноса данных) в **сервисе ETL**:
    - `docker compose exec -it etl_from_postgres_to_es python sqlite_to_postgres/load_data.py`
- использовать ETL сервис `etl_from_postgres_to_es` для постоянной выгрузки данных из **PostgreSQL** и загрузки в **Elastisearch**.
- создать партицированные таблицы через контейнер базы данных Auth сервиса - `auth_db`:
    - `docker compose exec -it auth_db psql -U $(echo $POSTGRES_USER) -d $(echo $POSTGRES_DB) -f create_partition_table_entry_histories.ddl`
- для **запуска тестов** Async API необходимо запустить docker-compose.py в директории `./async_api/src/tests/functional/`
