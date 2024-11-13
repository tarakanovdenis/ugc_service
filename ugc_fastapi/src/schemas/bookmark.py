from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class BookmarkBase(BaseModel):
    film_ids: list[UUID]
    user_id: UUID

    class Config:
        str_strip_whitespace = True


class BookmarkRead(BookmarkBase):
    id: UUID
    created_at: datetime
