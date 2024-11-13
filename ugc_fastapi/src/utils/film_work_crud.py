from uuid import UUID

from fastapi import (
    HTTPException,
    status,
    Request
)

# from beanie import DeleteRules
from beanie.odm.fields import DeleteRules
from src.models.rating import Rating
from src.models.review import Review
from src.models.film_work import FilmWork
from src.models.bookmark import Bookmark
from src.utils.utils import (
    SortingByCreationTime,
)
from src.schemas.film_work import (
    FilmWorkCreate,
    # FilmWorkRead,
    FilmWorkUpdate
)
from src.services import rabbitmq


async def get_films(sort: SortingByCreationTime) -> list[FilmWork]:
    films = await FilmWork.find_all().sort(sort.value_for_sort_method).to_list()
    if not films:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Films were not found.'
        )
    return films


async def get_film_by_id(film_id: UUID) -> FilmWork:
    film = await FilmWork.find_one(FilmWork.id == film_id)

    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Film with the specified ID was not found.'
        )
    return film


async def create_film(
    request: Request,
    film_in: FilmWorkCreate
) -> FilmWork:
    film = FilmWork(**film_in.model_dump())
    created_film: FilmWork = await film.create()

    rabbitmq.send_message_using_routing_key(
        # connection=rabbitmq.rabbitmq_connection,
        # channel=rabbitmq.rabbitmq_channel,
        exchange_name=rabbitmq.FilmExchange.EXCHANGE_NAME.value,
        routing_key=rabbitmq.FilmExchange.CREATING_FILM_ROUTING_KEY.value,
        message={
            'film_id': str(created_film.id),
            'title': created_film.title,
            'description': created_film.description
        }
    )

    return created_film


async def update_film(
    film_id: UUID,
    film_update: FilmWorkUpdate
) -> FilmWork:
    film = await get_film_by_id(film_id)

    update_query = {
        '$set': {
            field: value for field, value in film_update.model_dump(exclude_unset=True).items()
        }
    }
    updated_film = await film.update(update_query)

    return updated_film


async def delete_film(
    film_id: UUID
):
    film = await get_film_by_id(film_id)

    try:
        await film.delete(link_rule=DeleteRules.DELETE_LINKS)
        await Rating.find(Rating.film_id == film.id).delete()
        await Review.find(Review.film_id == film.id).delete()
        await Bookmark.find_all().update(
            {
                '$pull': {'film_ids': film.id}
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong...'
        )
