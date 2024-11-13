from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class ProjectSettings(BaseModel):
    title: str = "Auth Service"
    description: str = (
        "Here it can be found information about the endpoints"
        "and data types of the available schemes of the endpoints"
    )
    docs_url: str = "/auth/docs"
    openapi_url: str = "/auth/openapi.json"
    version: str = "0.1.0"
    domain_name: str = "http://localhost:8000"


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60
    reset_password_token_expire_minutes: int = 5


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore"
    )


class ServiceSettings(EnvSettings):
    # Database settings
    postgres_user: str = Field(default="app")
    postgres_password: str = Field(default="123qwe")
    postgres_db: str = Field(default="auth_database")
    postgres_host: str = Field(default="auth_db")
    postgres_port: int = Field(default=5432)

    db_echo: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    # RabbitMQ settings
    rabbitmq_host: str = Field(default="rabbitmq")
    rabbitmq_port: int = Field(default=5672)
    rabbitmq_username: str = Field(default="username")
    rabbitmq_password: str = Field(default="password")

    # Redis settings
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)

    jaeger_host: str = Field(default="jaeger")
    jaeger_port: int = Field(default=6831)
    jaeger_console_output: bool = Field(default=False)
    jaeger_configure_tracer: bool = Field(default=False)  # Set to True to allow Jaeger tracing
    otel_resource_attributes: str = Field(
        default="service.name=Authentication Service"
    )


class OAuthSettings(BaseSettings):
    oauth_provider: str = 'google'
    oauth_client_id: str = '1065143737604-mqo6qe5rhq167ivoe8bi90nupmhavrv5.apps.googleusercontent.com'
    oauth_client_secret: str = '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'
    # authorization_url: str = ...
    oauth_google_server_metadata_url: str = 'https://accounts.google.com/.well-known/openid-configuration'


class Settings(BaseSettings):
    project_settings: ProjectSettings = ProjectSettings()
    service_settings: ServiceSettings = ServiceSettings()
    jwt_settings: AuthJWT = AuthJWT()

    REQUEST_LIMIT_PER_MINUTE: int = 20

    oauth_settings: OAuthSettings = OAuthSettings()

    # Database engine settings
    db_url: str = (
        f"postgresql+asyncpg://{service_settings.postgres_user}"
        f":{service_settings.postgres_password}@{service_settings.postgres_host}"
        f":{service_settings.postgres_port}/{service_settings.postgres_db}"
    )


settings = Settings()
