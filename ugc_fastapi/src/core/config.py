from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'


class AuthJWT(BaseModel):
    public_key_path: Path = BASE_DIR / 'certs' / 'public.pem'
    algorithm: str = 'RS256'


class Settings(BaseSettings):
    # MongoDB settings
    mongodb_host: str
    mongodb_port: int
    mongodb_db_name: str

    # JWT settings
    jwt_settings: AuthJWT = AuthJWT()

    # RabbitMQ
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_username: str
    rabbitmq_password: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding='utf-8'
    )
    # class Config:
    #     env_file = ENV_FILE_PATH


settings = Settings()
