from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
import json

import aio_pika

from src.core.config import settings


if TYPE_CHECKING:
    from aio_pika import Connection, Channel
    from aio_pika.abc import (
        AbstractRobustConnection,
    )


class UserActivityExchange(Enum):
    EXCHANGE_NAME = 'user-reporting'
    REGISTRATION_ACTIVITY_ROUTING_KEY = 'user-reporting.v1.registered'
    EDITING_INFO_ACTIVITY_ROUTING_KEY = 'user-reporting.v1.edited'
    DELETING_ACTIVITY_ROUTING_KEY = 'user-reporting.v1.deleted'
    PASSWORD_RESET_ACTIVITY_ROUTING_KEY = 'user-reporting.v1.password_reset'


async def get_rabbitmq_connection(
    username: str = settings.service_settings.rabbitmq_username,
    password: str = settings.service_settings.rabbitmq_password,
    host: str = settings.service_settings.rabbitmq_host,
    port: int = settings.service_settings.rabbitmq_port
) -> AbstractRobustConnection:
    connection: Connection = await aio_pika.connect_robust(
        host=host,
        port=port,
        login=username,
        password=password,
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
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key=routing_key)

        await channel.close()
        await connection.close()
