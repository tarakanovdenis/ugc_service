from fastapi import (
    APIRouter,
    Response,
    Depends
)

from src.dependencies import security_jwt
from src.schemas.message import (
    MessageSchemaForAllUsers,
    MessageSchemaForSpecificUsers,
    MessageSchemaForSpecificUser,
)
from src.services.rabbitmq import (
    send_message_using_routing_key,
    UserOfferNotification
)
from src.utils.messages import messages


router = APIRouter(
    dependencies=[Depends(security_jwt)]
)


@router.post("/users/")
async def notify_all_users(
    message: MessageSchemaForAllUsers
):
    '''
    Send a notification to all users

    Parameters:
    - **message**: a message containing metadata, notification information
    and delivery method
    '''
    if message.delivery_method == 'email':
        await send_message_using_routing_key(
            UserOfferNotification.EXCHANGE_NAME.value,
            UserOfferNotification.SPECIAL_OFFER_ROUTING_KEY.value,
            message
        )
    return Response(
        status_code=200,
        content={
            "details": messages.MESSAGE_WAS_SENT,
        },
    )


@router.post("/users/subcribers/")
async def notify_specific_users(
    message: MessageSchemaForSpecificUsers
):
    '''
    Send a notification to specific users (for example, subcribers) about
    the release of the movie

    Parameters:
    - **message**: a message containing metadata, information about the movie
    and delivery method, list of user ids
    '''
    if message.delivery_method == 'email':
        await send_message_using_routing_key(
            UserOfferNotification.EXCHANGE_NAME.value,
            UserOfferNotification.SPECIAL_OFFER_ROUTING_KEY.value,
            message
        )

    return Response(
        status_code=200,
        content={
            "details": messages.MESSAGE_WAS_SENT
        },
    )


@router.post("/user/")
async def notify_specific_user(
    message: MessageSchemaForSpecificUser
):
    '''
    Send a notification to the specific user

    Parameters:
    - **message**: a message containing metadata, notification information
    and delivery method
    '''
    if message.delivery_method == 'email':
        await send_message_using_routing_key(
            UserOfferNotification.EXCHANGE_NAME.value,
            UserOfferNotification.SPECIAL_OFFER_ROUTING_KEY.value,
            message
        )

    return Response(
        status_code=200,
        content={
            "details": messages.MESSAGE_WAS_SENT,
        },
    )
