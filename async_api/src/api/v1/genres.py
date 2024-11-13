from http import HTTPStatus

from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Path,
    Depends,
    Request,
    Response,
    HTTPException,
    BackgroundTasks,
)
from src.services.genre import GenreService, get_genre_service
from src.models.models import Genre
from src.api.v1.films import get_pagination_params
from src.utils.auth_jwt_dependency import security_jwt
from src.utils.producer import (
    AsyncAPITopics,
    GenreTopicPartitions,
    send_message_task,
)


router = APIRouter(dependencies=[Depends(security_jwt)])


@router.get(
    '/',
    response_model=Optional[list[Genre]],
    summary='Get genres'
)
async def genres(
    request: Request,
    background_tasks: BackgroundTasks,
    pagination: Annotated[dict, Depends(get_pagination_params)],
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Get genre list:

    Parameters:
    - **pagination**: a dependency that returns the pagination parameters -
        page_number (int, default=0), page_size (int, default=10)

    Return value:
    - **genres** (Optional[list[Genre]])
    """
    page_number = pagination['page_number']
    page_size = pagination['page_size']

    genres = await genre_service.get_genres(
        page_number,
        page_size
    )
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genres not found'
        )

    background_tasks.add_task(
        send_message_task,
        request,
        router,
        AsyncAPITopics.GENRE_TOPIC.value,
        GenreTopicPartitions.GET_GENRES.value,
        query_parameters={
            'page_number': page_number,
            'page_size': page_size
        }
    )

    return genres


@router.get(
    '/{genre_id}',
    response_model=Optional[Genre],
    response_model_exclude={
        'description',
    },
    summary='Get genre details by genre id'
)
async def genre_details(
    request: Request,
    background_tasks: BackgroundTasks,
    response: Response,
    genre_id: Annotated[str, Path(default=...)],
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Get genre details by genre id:

    Parameters:
    - **genre_id** (str): genre id

    Return value:
    - **genre** (Optional[Genre]): genre with the following fields: id, name
    """

    genre = await genre_service.get_genre_by_id(genre_id, response)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genre not found'
        )

    background_tasks.add_task(
        send_message_task,
        request,
        router,
        AsyncAPITopics.GENRE_TOPIC.value,
        GenreTopicPartitions.GET_GENRE_BY_ID.value,
        query_parameters={
            'genre_id': genre_id
        }
    )

    return genre
