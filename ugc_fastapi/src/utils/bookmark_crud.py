from uuid import UUID

from fastapi import (
    HTTPException,
    status
)
from pymongo.errors import DuplicateKeyError

from src.models.bookmark import Bookmark
from src.models.film_work import FilmWork
from src.utils import film_work_crud
from src.utils.utils import SortingByCreationTime
from src.utils.film_work_crud import get_film_by_id


async def get_bookmark_by_id(bookmark_id: UUID):
    bookmark = await Bookmark.find_one(Bookmark.id == bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Bookmark was not found'
        )
    return bookmark


async def create_bookmark_by_user_id(user_id: UUID) -> Bookmark:
    try:
        user_bookmark = Bookmark(user_id=user_id)
        return await user_bookmark.create()
    except DuplicateKeyError:
        return {
            'message': f'User with ID {user_id.hex} already has bookmark'
        }


async def get_bookmark_by_user_id(user_id: UUID) -> Bookmark:
    bookmark = await Bookmark.find_one(
        Bookmark.user_id == user_id
    )
    if not bookmark:
        bookmark = await create_bookmark_by_user_id(user_id)
    return bookmark


async def add_film_to_the_user_bookmark(user_id, film_id):
    film = await film_work_crud.get_film_by_id(film_id)
    bookmark = await get_bookmark_by_user_id(user_id)

    bookmark.film_ids.append(film.id)

    return await bookmark.save()


async def get_user_bookmark_films(
    user_id: UUID,
    sort: SortingByCreationTime,
) -> list[FilmWork]:
    bookmark = await get_bookmark_by_user_id(user_id)
    films = await FilmWork.find(
        {
            '_id': {'$in': bookmark.film_ids}
        }
    ).sort(sort.value_for_sort_method).to_list()
    return films


async def delete_user_bookmark_by_user_id(user_id: UUID):
    bookmark = await get_bookmark_by_user_id(user_id)
    await bookmark.delete()


async def delete_film_uuid_from_user_bookmark(user_id: UUID, film_id: UUID):
    bookmark = await get_bookmark_by_user_id(user_id)
    film = await get_film_by_id(film_id)

    updated_bookmark = await bookmark.update(
        {
            '$pull': {'film_ids': film.id}
        }
    )

    return updated_bookmark
