from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Rating(Document):
    id: UUID = Field(default_factory=uuid4)
    rating: int = Field(ge=1, le=10)
    user_id: UUID
    film_id: UUID
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = 'ratings'

    class Config:
        str_strip_whitespace = True
        json_schema_extra = {
            'example': {
                'id': uuid4(),
                'rating': 10.0,
                'user_id': uuid4(),
                'film_id': uuid4(),
                'created_at': datetime.now(timezone.utc)
            }
        }
