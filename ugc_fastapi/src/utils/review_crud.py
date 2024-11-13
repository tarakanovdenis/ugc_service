from uuid import UUID

from beanie import WriteRules
from fastapi import (
    HTTPException,
    status
)

from src.models.film_work import FilmWork
from src.models.review import Review
from src.utils.utils import (
    SortingByCreationTime,
)
from src.schemas.review import (
    ReviewCreate,
    ReviewUpdate
)
from src.utils import film_work_crud


async def add_review_to_film(
    user_id: UUID,
    film_id: UUID,
    review_in: ReviewCreate,
) -> Review:
    film: FilmWork = await film_work_crud.get_film_by_id(film_id)

    review_in_dict = review_in.model_dump()
    review_in_dict['film_id'] = film_id
    review_in_dict['user_id'] = user_id

    review = Review(**review_in_dict)

    film.reviews.append(review)

    await film.save(link_rule=WriteRules.WRITE)

    return await review.create()


async def get_review_by_id(review_id: UUID) -> Review:
    review = await Review.find_one(Review.id == review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review with specified ID was not found.'
        )

    return review


async def get_all_reviews(sort: SortingByCreationTime) -> list[Review]:
    reviews = await Review.find_all().sort(
        sort.value_for_sort_method
    ).to_list()
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Reviews were not found.'
        )
    return reviews


async def get_film_reviews(
    sort: SortingByCreationTime,
    film_id: UUID,
) -> list[Review]:
    reviews = await Review.find(
        Review.film_id == film_id
    ).sort(sort.value_for_sort_method).to_list()
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Reviews were not found.'
        )
    return reviews


async def get_user_reviews(
    sort: SortingByCreationTime,
    user_id: UUID,
) -> list[Review]:
    user_reviews = await Review.find(
        Review.user_id == user_id
    ).sort(sort.value_for_sort_method).to_list()

    if not user_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Reviews were not found.'
        )
    return user_reviews


async def update_review(
    review_id: UUID,
    user_id: UUID,
    review_update: ReviewUpdate
) -> Review:
    review = await get_review_by_id(review_id)

    if review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don\'t have the permissions to edit this review.'
        )

    update_query = {
        '$set': {
            field: value for field, value in review_update.model_dump(exclude_unset=True).items()
        }
    }

    try:
        updated_review: Review = await review.update(update_query)

        # Using result we can find out whether the changing of FilmWork record
        _ = await FilmWork.find_one(
            FilmWork.id == updated_review.film_id
        ).update(
            {
                '$set': {'reviews.$[element]': updated_review},
            },
            array_filters=[{'element._id': review.id}]
        )
        return updated_review
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong...'
        )


async def delete_review(
    review_id: UUID,
    user_id
):
    review = await get_review_by_id(review_id)

    if review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You don\t have the permissions to edit this review.'
        )

    try:
        await review.delete()
        await FilmWork.find_one(
            FilmWork.id == review.film_id
        ).update(
            {
                '$pull': {'reviews': {'_id': review.id}}
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong...'
        )
