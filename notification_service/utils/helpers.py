import json

from sqlalchemy import Result
from redis import Redis

from schemas.user import User


USER_EMAILS_CACHE_EXPIRE_IN_SECONDS = 360


def convert_user_orm_to_user_dto(
    users_orm: Result
) -> list[User]:
    users_dto = [
        User.model_validate(orm_object, from_attributes=True) for orm_object in users_orm
    ]
    return users_dto


def get_email_user_list(users_dto: list[User]):
    user_email_list = [
        user.model_dump()['email'] for user in users_dto
    ]
    return user_email_list


def put_user_email_list_to_cache(redis: Redis, user_email_list):
    redis.set(
        'user_email_list',
        json.dumps(user_email_list),
        USER_EMAILS_CACHE_EXPIRE_IN_SECONDS
    )


def get_user_email_list_from_cache(redis: Redis):
    user_email_list = redis.get('user_email_list')
    if not user_email_list:
        return None
