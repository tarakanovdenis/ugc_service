from uuid import UUID
from datetime import datetime

from pydantic import BaseModel  # , ConfigDict


class ReviewBase(BaseModel):
    title: str | None = None
    body: str | None = None

    class Config:
        str_strip_whitespace = True


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: UUID
    film_id: UUID
    user_id: UUID
    created_at: datetime


class ReviewUpdate(ReviewBase):
    pass
