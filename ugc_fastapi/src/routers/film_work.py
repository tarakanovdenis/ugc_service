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

from src.models.film_work import FilmWork
from src.schemas.film_work import (
    FilmWorkCreate,
    FilmWorkRead,
    FilmWorkUpdate
)
from src.utils.utils import SortingByCreationTime
from src.utils import film_work_crud
from src.dependencies import security_jwt


router = APIRouter(
    dependencies=[Depends(security_jwt)]
)


@router.post(
    '/',
    response_description='Film record was added to the database',
    status_code=status.HTTP_201_CREATED,
    response_model=FilmWorkRead
)
async def add_film_work(
    request: Request,
    film_in: FilmWorkCreate
):
    return await film_work_crud.create_film(request, film_in)


@router.get(
    '/',
    response_description='Film records retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=list[FilmWorkRead]
)
async def get_films(
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value
):
    return await film_work_crud.get_films(sort)


@router.get(
    '/{film_id}',
    response_description='Film record retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=FilmWorkRead
)
async def get_film_details(
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')]
):
    return await film_work_crud.get_film_by_id(film_id)


@router.patch(
    '/{film_id}',
    response_description='Film record was updated.',
    response_model=FilmWorkRead
)
async def update_film(
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')],
    film_update: FilmWorkUpdate
):
    return await film_work_crud.update_film(film_id, film_update)


@router.delete(
    '/{film_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_film(
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')]
):
    await film_work_crud.delete_film(film_id)
