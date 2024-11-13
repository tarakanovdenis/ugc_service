import json
from enum import Enum

from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
    BasicProperties,
    DeliveryMode
)
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from src.core.config import settings


class FilmExchange(Enum):
    EXCHANGE_NAME = 'film-reporting'
    CREATING_FILM_ROUTING_KEY = 'film-reporting.v1.created'
    EDIITING_FILM_ROUTING_KEY = 'film-reporting.v1.edited'
    DELETING_FILM_KEY = 'film-reporting.v1.deleted'


# rabbitmq_connection: BlockingConnection | None = None
# rabbitmq_channel: BlockingChannel | None = None

def get_rabbitmq_connection_channel(
    username: str = settings.rabbitmq_username,
    password: str = settings.rabbitmq_password,
    host: str = settings.rabbitmq_host,
    port: int = settings.rabbitmq_port,
):
    credentials = PlainCredentials(username=username, password=password)
    connection = BlockingConnection(
        ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )
    )
    channel = connection.channel()
    return connection, channel


def setup_rabbitmq(
) -> tuple[BlockingConnection, BlockingChannel]:
    connection, channel = get_rabbitmq_connection_channel()

    channel.exchange_declare(
        exchange=FilmExchange.EXCHANGE_NAME.value,
        exchange_type=ExchangeType.direct,
        durable=True
    )

    result = channel.queue_declare(
        queue=FilmExchange.CREATING_FILM_ROUTING_KEY.value,
        durable=True,
    )
    queue_name = result.method.queue

    channel.queue_bind(
        exchange=FilmExchange.EXCHANGE_NAME.value,
        queue=queue_name,
        routing_key=FilmExchange.CREATING_FILM_ROUTING_KEY.value
    )
    channel.close()
    connection.close()


def send_message_using_routing_key(
    # connection: BlockingConnection,
    # channel: BlockingChannel,
    exchange_name: str,
    routing_key: str,
    message: dict,
):
    connection, channel = get_rabbitmq_connection_channel()
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=BasicProperties(
            # content_type='',
            delivery_mode=DeliveryMode.Persistent
        )
    )
    channel.close()
    connection.close()
