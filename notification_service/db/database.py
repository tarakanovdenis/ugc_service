from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


engine = create_engine(
    f'postgresql+psycopg2://{settings.postgres_user}'
    f':{settings.postgres_password}@{settings.postgres_host}'
    f':{settings.postgres_port}/{settings.postgres_db}'
)

Session = sessionmaker(bind=engine)
