from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Path,
    Query,
    Depends,
    Request,
    Response,
    HTTPException,
    BackgroundTasks,
)

from src.services.person import PersonService, get_person_service
from src.models.models import Person
from src.api.v1.films import get_pagination_params
from src.utils.auth_jwt_dependency import security_jwt
from src.utils.producer import (
    AsyncAPITopics,
    PersonTopicPartitions,
    send_message_task,
)


router = APIRouter(dependencies=[Depends(security_jwt)])


@router.get(
    '/search',
    response_model=Optional[list[Person]],
    summary='Get persons by searching using keyword in the name of the person'
)
async def search_persons(
    request: Request,
    background_tasks: BackgroundTasks,
    pagination: Annotated[dict, Depends(get_pagination_params)],
    query: Annotated[str, Query(description='Person')] = None,
    person_service: PersonService = Depends(get_person_service),
):
    """
    Get person list:

    Parameters:
    - **query** (str): keyword to search a person
    - **pagination**: a dependency that returns the pagination parameters -
        page_number (int, default=0), page_size (int, default=10)
    Return value:
    - **persons** (Optional[list[Person]]): list of persons
    """

    page_number = pagination['page_number']
    page_size = pagination['page_size']

    persons = await person_service.search_persons(
        page_number,
        page_size,
        query,
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Persons not found'
        )

    background_tasks.add_task(
        send_message_task,
        request,
        router,
        AsyncAPITopics.PERSON_TOPIC.value,
        PersonTopicPartitions.SEARCH_PERSONS_BY_KEYWORD.value,
        query_parameters={
            'keyword_to_search': str(query),
            'page_number': page_number,
            'page_size': page_size
        }
    )

    return persons


@router.get(
    '/{person_id}',
    response_model=Optional[Person],
    summary='Get person details by person id'
)
async def person_details(
    request: Request,
    background_tasks: BackgroundTasks,
    response: Response,
    person_id: Annotated[str, Path(default=...)],
    person_service: PersonService = Depends(get_person_service)
):
    """
    Get person details by person id:

    Parameters:
    - **person_id** (str): person id

    Return value:
    - **person** (Optional[Person]): person with the following fields:
        id, full_name, films
    """

    person = await person_service.get_person_by_id(person_id, response)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Person not found'
        )

    background_tasks.add_task(
        send_message_task,
        request,
        router,
        AsyncAPITopics.PERSON_TOPIC.value,
        PersonTopicPartitions.GET_PERSON_BY_ID.value,
        query_parameters={
            'person_id': person_id,
        }
    )

    return person
