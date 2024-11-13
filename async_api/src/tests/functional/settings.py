from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.tests.functional.testdata.es_mappings import (
    es_movie_mappings,
    es_person_mappings,
    es_genre_mappings,
)
from src.tests.functional.testdata.es_settings import (
    es_movie_settings,
    es_person_settings,
    es_genre_settings,
)


BASE_DIR = Path(__file__).parent.parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class TestSettings(EnvSettings):
    es_host: str = Field(default="http://elasticsearch:9200")

    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)

    service_url: str = Field(default="http://async_api_backend_for_test:8000/")


class MovieTestSettings(TestSettings):
    es_index: str = Field(default='movies')
    es_index_mappings: dict = Field(default=es_movie_mappings)
    es_index_settings: dict = Field(default=es_movie_settings)


class PersonTestSettings(TestSettings):
    es_index: str = Field(default='persons')
    es_index_mappings: dict = Field(default=es_person_mappings)
    es_index_settings: dict = Field(default=es_person_settings)


class GenreTestSettings(TestSettings):
    es_index: str = Field(default='genres')
    es_index_mappings: dict = Field(default=es_genre_mappings)
    es_index_settings: dict = Field(default=es_genre_settings)


test_settings = TestSettings()
movie_test_settings = MovieTestSettings()
person_test_settings = PersonTestSettings()
genre_test_settings = GenreTestSettings()
