from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'


class Settings(BaseSettings):
    # RabbitMQ settings
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_username: str
    rabbitmq_password: str

    # Yandex SMTP settings
    yandex_login: str
    yandex_password: str
    yandex_smtp_host: str
    yandex_smtp_port: int
    yandex_domain: str = 'yandex.ru'

    # Gmail SMTP settings
    gmail_login: str
    gmail_password: str
    gmail_smtp_host: str
    gmail_smtp_port: int
    gmail_domain: str = 'gmail.com'

    # Email Sender Address
    sender_address: str

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
    project_name: str = 'Notification Service'

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding='utf-8'
    )

    auth_service_domain_name: str = 'http://localhost:8000'

settings = Settings()
