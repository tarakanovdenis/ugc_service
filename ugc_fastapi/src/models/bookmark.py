from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Annotated

from beanie import Document, Link, Indexed
from pydantic import Field

from src.models.film_work import FilmWork


class Bookmark(Document):
    id: UUID = Field(default_factory=uuid4)
    user_id: Annotated[UUID, Indexed(unique=True)]
    film_ids: list[UUID] | None = []
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = 'bookmarks'

    class Config:
        str_strip_whitespace = True
        json_schema_extra = {
            'example': {
                'id': uuid4(),
                'user_id': uuid4(),
                'films': list[FilmWork],
                'created_at': datetime.now(timezone.utc)
            }
        }
