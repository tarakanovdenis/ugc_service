from __future__ import annotations
from typing import TYPE_CHECKING
import json
from enum import Enum

import aio_pika

from src.core.config import settings


if TYPE_CHECKING:
    from aio_pika import Connection, Channel
    from aio_pika.abc import (
        AbstractRobustConnection,
    )


class UserOfferNotification(Enum):
    EXCHANGE_NAME = 'user-notifications'
    SPECIAL_OFFER_ROUTING_KEY = 'special-offer-reporting.v1.created'


class ReviewRatingExchange(Enum):
    EXCHANGE_NAME = 'film-review-reporting'
    RATING_FILM_REVIEW_ROUTING_KEY = 'film-review-rating-reporting.v1.created'


class FilmExchange(Enum):
    EXCHANGE_NAME = 'film-reporting'
    CREATING_FILM_ROUTING_KEY = 'film-reporting.v1.created'
    EDITING_FILM_ROUTING_KEY = 'film-reporting.v1.edited'
    DELETING_FILM_KEY = 'film-reporting.v1.deleted'


async def get_rabbitmq_connection(
    username: str = settings.rabbitmq_username,
    password: str = settings.rabbitmq_password,
    host: str = settings.rabbitmq_host,
    port: int = settings.rabbitmq_port
) -> AbstractRobustConnection:
    connection: Connection = await aio_pika.connect_robust(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_username,
        password=settings.rabbitmq_password
    )
    return connection


async def send_message_using_routing_key(
    exchange_name: str,
    routing_key: str,
    message: dict,
):
    connection = await get_rabbitmq_connection()

    async with connection:
        channel: Channel = await connection.channel()

        exchange = await channel.declare_exchange(
            exchange_name, type=aio_pika.ExchangeType.DIRECT,
        )
        message = aio_pika.Message(
            body=json.dumps(message),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key=routing_key)

        print(f'Message ({message!r} was sent successfully)')
        channel.close()
        connection.close()
