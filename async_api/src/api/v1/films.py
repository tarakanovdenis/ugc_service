from enum import Enum
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Path,
    Query,
    Request,
    Depends,
    Response,
    HTTPException,
    BackgroundTasks,
)
from src.services.film import FilmService, get_film_service
from src.models.models import Film
from src.utils.auth_jwt_dependency import security_jwt
from src.utils.producer import (
    AsyncAPITopics,
    FilmTopicPartitions,
    send_message_task,
)


router = APIRouter(dependencies=[Depends(security_jwt)])


class SortBy(str, Enum):
    DESC = 'In descending order of the rating'
    ASC = 'In ascending order of the rating'


def get_pagination_params(
    page_number: Annotated[int, Query(description='Page number', ge=0)] = 0,
    page_size: Annotated[
        int, Query(description='Number of objects per page', ge=0)
    ] = 10
):
    return {'page_number': page_number, 'page_size': page_size}


@router.get(
    '/',
    response_model=Optional[list[Film]],
    summary="Get films"
)
async def films(
    request: Request,
    background_tasks: BackgroundTasks,
    pagination: Annotated[dict, Depends(get_pagination_params)],
    genre: Annotated[str, Query(description='Film genre')] = None,
    sort: Annotated[SortBy, Query(description='Sort by')] = SortBy.DESC,
    film_service: FilmService = Depends(get_film_service),
):
    """
    Get film list:

    Parameters:
    - **genre** (str): choice a film genre
    - **sort**: sorting parameter
    - **pagination**: a dependency that returns the pagination parameters -
        page_number (int, default=0), page_size (int, default=10)

    Return value:
    - **films** (Optional[list[Film]]): list of films with the following
        fields: id, title, imdb_rating
    """

    page_number = pagination['page_number']
    page_size = pagination['page_size']

    films = await film_service.get_films(
        genre,
        page_number,
        page_size,
        sort.name
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Films not found'
        )

    background_tasks.add_task(
        send_message_task,
        request=request,
        router=router,
        topic=AsyncAPITopics.FILM_TOPIC.value,
        partition_key=FilmTopicPartitions.GET_FILMS.value,
        query_parameters={
            'genre': str(genre),
            'sort': sort,
            'page_number': page_number,
            'page_size': page_size
        }
    )

    return films


@router.get(
    '/search',
    response_model=Optional[list[Film]],
    summary='Get films by searching using keyword in the title or description'
)
async def search_films(
    request: Request,
    background_tasks: BackgroundTasks,
    pagination: Annotated[dict, Depends(get_pagination_params)],
    query: Annotated[str, Query(description='Keyword to search a film')] = None,
    genre: Annotated[str, Query(description='Film genre')] = None,
    sort: Annotated[SortBy, Query(description='Sort by')] = SortBy.DESC,
    film_service: FilmService = Depends(get_film_service),
):
    """
    Get film list:

    Parameters:
    - **query** (str): keyword to search a film
    - **genre** (str): choice a film genre
    - **sort**: sorting parameter
    - **pagination**: a dependency that returns the pagination parameters -
        page_number (int, default=0), page_size (int, default=10)

    Return value:
    - **films** (Optional[list[Film]]): list of films with the following
        fields: id, title, imdb_rating
    """

    page_number = pagination['page_number']
    page_size = pagination['page_size']

    films = await film_service.search_films(
        query,
        genre,
        page_number,
        page_size,
        sort.name
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Films not found'
        )

    background_tasks.add_task(
        send_message_task,
        request=request,
        router=router,
        topic=AsyncAPITopics.FILM_TOPIC.value,
        partition_key=FilmTopicPartitions.SEARCH_FILMS_BY_KEYWORD.value,
        query_parameters={
            'keyword_to_search': str(query),
            'genre': str(genre),
            'sort': sort,
            'page_number': page_number,
            'page_size': page_size
        }
    )

    return films


@router.get(
    '/{film_id}',
    response_model=Optional[Film],
    response_model_exclude={
        'actors_names',
        'directors_names',
        'writers_names'
    },
    summary='Get film details by film id'
)
async def film_details(
    request: Request,
    background_tasks: BackgroundTasks,
    response: Response,
    film_id: Annotated[str, Path(default=...)],
    film_service: FilmService = Depends(get_film_service)
):
    """
    Get film details by film id:

    Parameters:
    - **film_id** (str): film id

    Return value:
    - **film** (Optional[Film]): film with the following fields: id,
        title, imdb_rating, description, genre, actors, writers, directors
    """

    film = await film_service.get_film_by_id(film_id, response)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Film not found'
        )

    background_tasks.add_task(
        send_message_task,
        request=request,
        router=router,
        topic=AsyncAPITopics.FILM_TOPIC.value,
        partition_key=FilmTopicPartitions.GET_FILM_BY_ID.value,
        query_parameters={
            'film_id': film_id
        }
    )
    return film
