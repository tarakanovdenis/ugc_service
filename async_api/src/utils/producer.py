import json
from datetime import datetime, timezone
from enum import Enum

from fastapi import (
    Request,
    APIRouter
)
from aiokafka import AIOKafkaProducer

from src.core.config import settings


class AsyncAPITopics(Enum):
    FILM_TOPIC = 'tracking.async_api.films'
    GENRE_TOPIC = 'tracking.async_api.genres'
    PERSON_TOPIC = 'tracking.async_api.persons'


class FilmTopicPartitions(Enum):
    GET_FILMS = 'get_films'
    GET_FILM_BY_ID = 'get_film_by_id'
    SEARCH_FILMS_BY_KEYWORD = 'search_films_by_keyword'


class GenreTopicPartitions(Enum):
    GET_GENRES = 'get_genres'
    GET_GENRE_BY_ID = 'get_genre_by_id'


class PersonTopicPartitions(Enum):
    GET_PERSONS = 'get_persons'
    GET_PERSON_BY_ID = 'get_person_by_id'
    SEARCH_PERSONS_BY_KEYWORD = 'search_persons_by_keyword'


async def send_one_message_to_kafka(topic: str, partition_key: str, body: dict):
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_settings.bootstrap_servers,
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    try:
        await producer.send_and_wait(
            topic,
            value=body,
            partition=None,
            key=partition_key
        )
    finally:
        await producer.stop()


async def send_message_task(
    request: Request,
    router: APIRouter,
    topic: str,
    partition_key: str,
    query_parameters: dict
):
    decoded_token_from_http_header = await router.dependencies[0].dependency(request)
    message_data = {
        'user_id': decoded_token_from_http_header['user_id'],
        'query_parameters': query_parameters,
        'visited_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %z')
    }
    await send_one_message_to_kafka(
        topic,
        partition_key=partition_key,
        body=message_data
    )