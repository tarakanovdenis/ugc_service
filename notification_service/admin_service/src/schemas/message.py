from uuid import UUID

from pydantic import BaseModel
from datetime import datetime


class IdMixin(BaseModel):
    id: UUID


class User(IdMixin):
    pass


class Review(IdMixin):
    author: User
    film_id: UUID


class ReviewRating(IdMixin):
    user: User
    review: Review
    rating: int


class FilmWork(IdMixin):
    title: str
    description: str


class MessageSchemaBase(IdMixin):
    title: str
    description: str

    delivery_method: str
    scheduled_date: datetime


class MessageSchemaForAllUsers(MessageSchemaBase):
    pass


class MessageSchemaForSpecificUser(MessageSchemaBase):
    user_id: User


class MessageSchemaForSpecificUsers(MessageSchemaBase):
    user_ids: list[User]


class MessageUserAboutRatingReview(IdMixin):
    user: User
    rating: ReviewRating
