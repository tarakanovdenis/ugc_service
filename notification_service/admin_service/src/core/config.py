from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'


class AuthJWT(BaseModel):
    public_key_path: Path = BASE_DIR / 'certs' / 'public.pem'
    algorithm: str = 'RS256'


class Settings(BaseSettings):
    # JWT settings
    jwt_settings: AuthJWT = AuthJWT()

    # RabbitMQ settings
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_username: str
    rabbitmq_password: str

    # Database settings
    postgres_user: str
    postgres_db: str
    postgres_password: str
    postgres_host: str
    postgres_port: str

    # Redis settings
    redis_host: str
    redis_port: int

    # FastAPI settings
    project_name: str = 'Admin Panel for the Notification Service'

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding='utf-8'
    )


settings = Settings()
