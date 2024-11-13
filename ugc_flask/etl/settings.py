import os
from enum import Enum

from dotenv import load_dotenv


load_dotenv()

CLICKHOUSE_CLUSTER = os.getenv('CLICKHOUSE_CLUSTER')
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST')
BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS')


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
    GET_PERSON_BY_ID = 'get_person_by_id'
    SEARCH_PERSONS_BY_KEYWORD = 'search_persons_by_keyword'


class ClickTrackingTopics(Enum):
    QUALITY_CHANGE_CLICK = 'tracking.clicks_on_video.quality_changes'
    PAUSE_CLICK = 'tracking.clicks_on_video.pauses'
    FULL_VIEW = 'tracking.clicks_on_video.full_views'


TOPIC_NAMES = [
    # Tracking clicks on the video
    ClickTrackingTopics.QUALITY_CHANGE_CLICK.value,
    ClickTrackingTopics.PAUSE_CLICK.value,
    ClickTrackingTopics.FULL_VIEW.value,

    # Tracking Async API Service page views
    AsyncAPITopics.FILM_TOPIC.value,
    AsyncAPITopics.GENRE_TOPIC.value,
    AsyncAPITopics.PERSON_TOPIC.value
]

# ClickHouse settings
CLICKHOUSE_DATABASE_NAME = 'tracking_user_events'
