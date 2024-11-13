from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class ProjectSettings(BaseModel):
    title: str = "Async API Service"
    description: str = (
        "Here it can be found information about the endpoints"
        " and data types of the available schemes of the endpoints"
    )
    docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    version: str = "0.1.0"


class AuthJWT(BaseModel):
    public_key_path: Path = BASE_DIR / "certs" / "public.pem"
    algorithm: str = "RS256"


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RedisSettings(EnvSettings):
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)


class ElasticsearchSettings(EnvSettings):
    elasticsearch_host: str = Field(default="http://elasticsearch:9200")


class KafkaSettings(EnvSettings):
    bootstrap_servers: str = Field(default="kafka:9092")


class Settings(BaseSettings):
    project_settings: ProjectSettings = ProjectSettings()
    redis_settings: RedisSettings = RedisSettings()
    es_settings: ElasticsearchSettings = ElasticsearchSettings()
    kafka_settings: KafkaSettings = KafkaSettings()
    jwt_settings: AuthJWT = AuthJWT()


settings = Settings()
