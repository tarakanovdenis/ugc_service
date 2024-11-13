from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

class DatabaseSettings(EnvSettings):
    # PostgreSQL
    postgres_db: str = Field(default="async_api_database")
    postgres_user: str = Field(default="app")
    postgres_password: str = Field(default="123qwe")
    postgres_host: str = Field(default="postgres_db")
    postgres_port: str = Field(default=5432)


class ElasticsearchSettings(EnvSettings):
    elasticsearch_host: str = Field(default="http://elasticsearch:9200")


class Settings(BaseSettings):
    db_settings: DatabaseSettings = DatabaseSettings()
    es_settings: ElasticsearchSettings = ElasticsearchSettings()


settings = Settings()

# Определить Data Source Name для подключения к базе данных (БД)
DSN = {
    'dbname': settings.db_settings.postgres_db,
    'user': settings.db_settings.postgres_user,
    'password': settings.db_settings.postgres_password,
    'host': settings.db_settings.postgres_host,
    'port': settings.db_settings.postgres_port,
}

# Настройки для процесса извлечения данных из БД

# Определить название файла в формате json для сохранения состояния
FILE_PATH = 'postgres_to_es/state_storage.json'

# Определить названия подхранилищ для имеющихся таблиц: film_work, person,
# genre. Состояние будет сохраняться для каждого подхранилища при работе
# с соответствующей таблицей
FILM_WORKS_SUBSTORAGE = 'film_works'
PERSONS_SUBSTORAGE = 'persons'
GENRES_SUBSTORAGE = 'genres'
SUBSTORAGES = [FILM_WORKS_SUBSTORAGE, PERSONS_SUBSTORAGE, GENRES_SUBSTORAGE]

# Настройки для процесса загрузки данных в Elasticsearch (ES)

# Определить время, с которого необходимо определять обновленные записи
# в таблицах, и ограничение количества выгружаемых записей
MODIFIED_TIME = '2020-01-01'
ROW_LIMIT = 200

# Определить путь к файлу, содержащему схему данных индекса ES
FILE_PATH_TO_ES_SCHEMA = 'postgres_to_es/es_schema.json'

# Определить наименование индекса в ES
MOVIES_INDEX_NAME = 'movies'
GENRES_INDEX_NAME = 'genres'
PERSONS_INDEX_NAME = 'persons'

# Определить время, через которое планировщик задач будет
# запускать ETL-процесс, сек.
SCHEDULER_TIME_INTERVAL = 10
