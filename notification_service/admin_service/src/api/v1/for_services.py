from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends
)

from src.dependencies import security_jwt
from src.schemas.message import (
    MessageSchemaForAllUsers,
    MessageSchemaForSpecificUsers,
    MessageUserAboutRatingReview
)
from src.services.rabbitmq import (
    send_message_using_routing_key,
    FilmExchange,
    ReviewRatingExchange
)
from src.utils.messages import messages


router = APIRouter(
    dependencies=[Depends(security_jwt)]
)


@router.post("/notify/film/users/")
async def notify_all_users_about_film_release(
    message: MessageSchemaForAllUsers
):
    '''
    Send a notification to all users about the release of the movie

    Parameters:
    - **message**: a message containing metadata, information about the movie
    and delivery method
    '''
    if message.delivery_method == 'email':
        await send_message_using_routing_key(
            FilmExchange.EXCHANGE_NAME.value,
            FilmExchange.EDITING_FILM_ROUTING_KEY.value,
            message
        )
    return Response(
        status_code=200,
        content={
            "details": messages.MESSAGE_WAS_SENT,
        },
    )


@router.post("/notify/film/users/subcribers/")
async def notify_specific_users_about_film_release(
    message: MessageSchemaForSpecificUsers
):
    '''
    Send a notification to specific users (for example, subcribers) about
    the release of the movie

    Parameters:
    - **message**: a message containing metadata, information about the movie
    and delivery method, list of users
    '''
    if message.delivery_method == 'email':
        await send_message_using_routing_key(
            FilmExchange.EXCHANGE_NAME.value,
            FilmExchange.EDITING_FILM_ROUTING_KEY.value,
            message
        )
    return Response(
        status_code=200,
        content={
            "details": messages.MESSAGE_WAS_SENT
        },
    )


@router.post("/notify/film/reviews/rating/")
async def notify_specific_user_about_film_release(
    message: MessageUserAboutRatingReview
):
    '''
    Send a notification to the specific user about the rating
    of the user's review

    Parameters:
    - **message**: a message containing metadata, information about
    the review rating and delivery method, user
    '''
    if message.delivery_method == 'email':
        await send_message_using_routing_key(
            ReviewRatingExchange.EXCHANGE_NAME.value,
            ReviewRatingExchange.RATING_FILM_REVIEW_ROUTING_KEY.value,
            message
        )
    return Response(
        status_code=200,
        content={
            "details": messages.MESSAGE_WAS_SENT
        },
    )
