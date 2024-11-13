from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Review(Document):
    id: UUID = Field(default_factory=uuid4)
    title: str
    body: str
    film_id: UUID
    user_id: UUID
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = 'reviews'

    class Config:
        str_strip_whitespace = True
        json_schema_extra = {
            'example': {
                'id': uuid4(),
                'title': 'Review title',
                'body': 'Some long text about the film.',
                'user_id': uuid4(),
                'created_at': datetime.now(timezone.utc)
            }
        }
