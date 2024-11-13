from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    status,
    Path,
    Query,
    Request,
    Depends
)

from src.schemas.rating import (
    RatingCreate,
    RatingRead,
    RatingUpdate,
    AvgRatingValue
)

from src.utils import rating_crud
from src.utils.utils import SortingByCreationTime
from src.dependencies import security_jwt


router = APIRouter(
    dependencies=[Depends(security_jwt)]
)


@router.post(
    '/{film_id}',
    response_description='Rating record was added to the database',
    status_code=status.HTTP_201_CREATED,
    response_model=RatingRead
)
async def add_rating_to_film(
    request: Request,
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')],
    rating_in: RatingCreate,
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await rating_crud.add_rating_to_film(user_id, film_id, rating_in)


@router.get(
    '/{film_id}/film',
    response_description='Average rating value of the film with the specified ID',
    status_code=status.HTTP_200_OK,
    response_model=AvgRatingValue,
)
async def get_film_average_rating_value(
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')]
):
    return await rating_crud.get_film_avg_rating_value(film_id)


@router.get(
    '/{film_id}/films',
    response_description='Rating records of the film with the specified ID',
    status_code=status.HTTP_200_OK,
    response_model=list[RatingRead],
)
async def get_film_ratings(
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')]
):
    return await rating_crud.get_film_ratings(film_id)


@router.get(
    '/{rating_id}',
    response_description='Rating record was retrieved',
    status_code=status.HTTP_200_OK,
    response_model=RatingRead,
)
async def get_rating_details(
    rating_id: Annotated[UUID, Path(description='Rating ID (UUID4)')]
):
    return await rating_crud.get_rating_by_id(rating_id)


@router.get(
    '/{user_id}/users',
    response_description='Rating records of the user with the spicified ID were retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=list[RatingRead],
)
async def get_user_ratings(
    request: Request,
    user_id: Annotated[UUID, Path(description='User ID (UUID4)')],
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await rating_crud.get_user_ratings(user_id, sort)


@router.get(
    '/me/users',
    response_description='Rating records of the user were retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=list[RatingRead],
)
async def get_user_own_ratings(
    request: Request,
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = decoded_token_from_http_header['user_id']

    return await rating_crud.get_user_ratings(user_id, sort)


@router.patch(
    '/{rating_id}',
    response_description='Rating record was successfully updated.',
    status_code=status.HTTP_200_OK,
    response_model=RatingRead
)
async def update_rating(
    request: Request,
    rating_id: Annotated[UUID, Path(description='Rating ID (UUID4)')],
    rating_update: RatingUpdate,
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = decoded_token_from_http_header['user_id']

    return await rating_crud.update_rating(user_id, rating_id, rating_update)


@router.delete(
    '/{rating_id}',
    response_description='Rating record was successfully deleted.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rating(
    request: Request,
    rating_id: Annotated[UUID, Path(description='Rating ID (UUID4)')],
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = decoded_token_from_http_header['user_id']

    return await rating_crud.delete_rating(rating_id, user_id)
