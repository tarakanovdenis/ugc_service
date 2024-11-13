from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class RatingBase(BaseModel):
    rating: int = Field(ge=1, le=10)

    class Config:
        str_strip_whitespace = True


class RatingCreate(RatingBase):
    pass


class RatingRead(RatingBase):
    id: UUID
    user_id: UUID
    film_id: UUID
    created_at: datetime


class RatingUpdate(RatingBase):
    pass


class AvgRatingValue(BaseModel):
    avg_rating_value: float
