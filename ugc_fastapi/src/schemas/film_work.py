from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from src.schemas.review import ReviewRead
from src.schemas.rating import RatingRead


class FilmWorkBase(BaseModel):
    title: str
    description: str | None

    class Config:
        str_strip_whitespace = True


class FilmWorkCreate(FilmWorkBase):
    pass


class FilmWorkRead(FilmWorkBase):
    id: UUID
    ratings: list[RatingRead] | None
    reviews: list[ReviewRead] | None
    created_at: datetime


class FilmWorkUpdate(FilmWorkBase):
    pass
