from uuid import UUID

from beanie import WriteRules
from fastapi import HTTPException, status

from src.models.film_work import FilmWork
from src.models.rating import Rating
from src.utils import film_work_crud
from src.utils.utils import SortingByCreationTime
from src.schemas.rating import (
    RatingCreate,
    RatingUpdate,
    AvgRatingValue
)


async def add_rating_to_film(
    user_id: UUID,
    film_id: UUID,
    rating_in: RatingCreate,
) -> Rating:
    film: FilmWork = await film_work_crud.get_film_by_id(film_id)

    rating_in_dict = rating_in.model_dump()
    rating_in_dict['user_id'] = user_id
    rating_in_dict['film_id'] = film_id

    rating = Rating(**rating_in_dict)

    film.ratings.append(rating)

    await film.save(link_rule=WriteRules.WRITE)
    return await rating.create()


async def get_film_avg_rating_value(
    film_id: UUID,
) -> AvgRatingValue:
    _ = await film_work_crud.get_film_by_id(film_id)

    avg_rating_value = await Rating.find(
        Rating.film_id == film_id
    ).avg(Rating.rating)

    avg_rating_value = AvgRatingValue(
        avg_rating_value=round(avg_rating_value, 1)
    )
    return avg_rating_value


async def get_film_ratings(
    film_id: UUID
):
    film = await film_work_crud.get_film_by_id(film_id)
    ratings: list[Rating] = film.ratings
    return ratings


async def get_rating_by_id(
    rating_id: UUID
) -> Rating:
    rating = await Rating.find_one(Rating.id == rating_id)

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Rating record with the specified ID was not found.'
        )
    return rating


async def get_user_ratings(
    user_id: UUID,
    sort: SortingByCreationTime,
) -> list[Rating]:
    user_ratings = await Rating.find(
        Rating.user_id == user_id
    ).sort(sort.value_for_sort_method).to_list()

    if not user_ratings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Rating records of the spicified user were not found.'
        )

    return user_ratings


async def update_rating(
    user_id: UUID,
    rating_id: UUID,
    rating_update: RatingUpdate,
):
    rating = await get_rating_by_id(rating_id)

    if rating.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don\t have the permissions to edit this rating.'
        )

    update_query = {
        '$set': {
            field: value for field, value in rating_update.model_dump(exclude_unset=True).items()
        }
    }

    try:
        updated_rating: Rating = await rating.update(update_query)

        # Using result we can find out whether the changing of FilmWork record
        _ = await FilmWork.find_one(
            FilmWork.id == updated_rating.film_id
        ).update(
            {
                '$set': {'ratings.$[element]': updated_rating},
            },
            array_filters=[{'element._id': rating.id}]
        )

        return updated_rating
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong...'
        )


async def delete_rating(
    rating_id: UUID,
    user_id: UUID,
):
    rating = await get_rating_by_id(rating_id)
    if rating.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don\t have the permissions to edit this rating.'
        )

    try:
        await rating.delete()
        await FilmWork.find_one(
            FilmWork.id == rating.film_id
        ).update(
            {
                '$pull': {'ratings': {'_id': rating.id}}
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong...'
        )
