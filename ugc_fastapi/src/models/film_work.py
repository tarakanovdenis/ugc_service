from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field

from src.models.review import Review
from src.models.rating import Rating


class FilmWork(Document):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str | None = None
    ratings: list[Link[Rating]] | None = []
    reviews: list[Link[Review]] | None = []
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = 'film_works'

    class Config:
        str_strip_whitespace = True
        json_schema_extra = {
            'example': {
                'id': uuid4(),
                'title': 'Star Wars',
                'description': 'Some description',
                'ratings': 7.7,
                'reviews': 'Review list',
                'created_at': datetime.now(timezone.utc)
            }
        }
