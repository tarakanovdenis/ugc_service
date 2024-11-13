from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    status,
    Path,
    Request,
    Query,
    Depends
)

from src.schemas.bookmark import BookmarkRead
from src.schemas.film_work import FilmWorkRead
from src.dependencies import security_jwt
from src.utils import bookmark_crud
from src.utils.utils import SortingByCreationTime


router = APIRouter(
    dependencies=[Depends(security_jwt)]
)


@router.post(
    '/',
    response_description='Bookmark record was added to the database',
    status_code=status.HTTP_201_CREATED,
    response_model=BookmarkRead
)
async def add_bookmark(
    request: Request,
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await bookmark_crud.create_bookmark_by_user_id(user_id)


@router.post(
    '/{film_id}/films',
    response_description='Film record with the specified ID was added to the bookmark',
    status_code=status.HTTP_201_CREATED,
    response_model=BookmarkRead
)
async def add_film_to_the_user_bookmark(
    request: Request,
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')]
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await bookmark_crud.add_film_to_the_user_bookmark(user_id, film_id)


@router.get(
    '/{user_id}/users',
    response_description='Bookmark record of the user was retrieved',
    status_code=status.HTTP_201_CREATED,
    response_model=BookmarkRead
)
async def get_user_bookmark(
    request: Request,
    user_id: Annotated[UUID, Path(description='User ID (UUID4)')]
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await bookmark_crud.get_bookmark_by_user_id(user_id)


@router.get(
    '/me/users/films',
    response_description='Films from own user bookmark were retrieved',
    status_code=status.HTTP_200_OK,
    response_model=list[FilmWorkRead],
)
async def get_films_from_own_user_bookmark(
    request: Request,
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await bookmark_crud.get_user_bookmark_films(user_id, sort)


@router.get(
    '/{user_id}/users/films',
    response_description='Films from the user bookmark were retrieved',
    response_model=list[FilmWorkRead]
)
async def get_user_bookmark_films(
    user_id: Annotated[UUID, Path(description='User')],
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value
):
    return await bookmark_crud.get_user_bookmark_films(user_id, sort)


@router.delete(
    '/{user_id}',
    response_description='Bookmark of the user was deleted',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_bookmark(
    user_id: Annotated[UUID, Path(description='User ID (UUID4)')]
):
    return bookmark_crud.delete_user_bookmark_by_user_id(user_id)


@router.delete(
    '/me/users/{film_id}/films',
    response_description='Film with the specified ID was delete from the user bookmark',
    status_code=status.HTTP_200_OK,
    response_model=BookmarkRead
)
async def delete_film_uuid_from_own_user_bookmark(
    request: Request,
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')],
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await bookmark_crud.delete_film_uuid_from_user_bookmark(user_id, film_id)


@router.delete(
    '/{user_id}/users/{film_id}/films',
    response_description='Film with the specified ID was delete from the user bookmark',
    status_code=status.HTTP_200_OK,
    response_model=BookmarkRead
)
async def delete_film_uuid_from_user_bookmark(
    user_id: Annotated[UUID, Path(description='User ID (UUID4)')],
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')],
):
    return await bookmark_crud.delete_film_uuid_from_user_bookmark(user_id, film_id)
