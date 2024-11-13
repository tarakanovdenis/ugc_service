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

from src.schemas.review import (
    ReviewCreate,
    ReviewRead,
    ReviewUpdate
)
from src.utils import review_crud
from src.utils.utils import SortingByCreationTime
from src.dependencies import security_jwt


router = APIRouter(
    dependencies=[Depends(security_jwt)]
)


@router.post(
    '/{film_id}',
    response_description='Review record was added to the database',
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewRead
)
async def add_review_to_film(
    request: Request,
    film_id: Annotated[UUID, Path(description='Film ID (UUID4)')],
    review_in: ReviewCreate,
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await review_crud.add_review_to_film(user_id, film_id, review_in)


@router.get(
    '/{review_id}',
    response_description='Review record retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=ReviewRead
)
async def get_review(
    review_id: Annotated[UUID, Path(description='Review ID (UUID)')]
):
    return await review_crud.get_review_by_id(review_id)


@router.get(
    '/',
    response_description='Review records retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=list[ReviewRead]
)
async def get_reviews(
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value
):
    return await review_crud.get_all_reviews(sort)


@router.get(
    '/{film_id}/films',
    response_description="Review records of film with specified ID were retrieved.",
    status_code=status.HTTP_200_OK,
    response_model=list[ReviewRead]
)
async def get_film_reviews(
    request: Request,
    film_id: Annotated[UUID, Path(description='Film ID (UUID)')],
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value,
):
    return await review_crud.get_film_reviews(sort, film_id)


@router.get(
    '/me/users',
    response_description='Review records of user were retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=list[ReviewRead]
)
async def get_user_reviews(
    request: Request,
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value,
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await review_crud.get_user_reviews(sort, user_id)


@router.get(
    '/{user_id}/users',
    response_description='Review records of user with specified ID were retrieved.',
    status_code=status.HTTP_200_OK,
    response_model=list[ReviewRead]
)
async def get_reviews_by_user_id(
    request: Request,
    user_id: Annotated[UUID, Path(description='User ID (UUID)')],
    sort: Annotated[SortingByCreationTime, Query(description='Sort')] = SortingByCreationTime.DESC.value,
):
    return await review_crud.get_user_reviews(sort, user_id)


@router.patch(
    '/{review_id}',
    response_description='Review record was updated.',
    status_code=status.HTTP_200_OK,
    response_model=ReviewRead
)
async def update_review_by_user(
    request: Request,
    review_id: Annotated[UUID, Path(description='Review ID (UUID)')],
    review_update: ReviewUpdate
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    return await review_crud.update_review(review_id, user_id, review_update)


@router.delete(
    '/{review_id}',
    response_description='Review record was deleted.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    request: Request,
    review_id: Annotated[UUID, Path(description='Review ID (UUID)')]
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    user_id = UUID(decoded_token_from_http_header['user_id'])

    await review_crud.delete_review(review_id, user_id)
