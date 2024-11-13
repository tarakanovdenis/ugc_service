import asyncio
from aiohttp import ClientSession

# from clickhouse_driver import Client
from aiokafka import AIOKafkaConsumer
from aiochclient import ChClient


import settings
import queries
from utils import (
    load_data_to_clickhouse_from_async_api_kafka_topics,
    load_data_to_clickhouse_from_video_events_kafka_topics
)


async def main():
    async with ClientSession() as session:
        client = ChClient(
            session=session,
            url=settings.CLICKHOUSE_HOST,
        )
        await client.execute(queries.drop_database)
        await client.execute(queries.create_database)

        # Table creating
        async def create_tables():
            for query in queries.table_creation_queries:
                await client.execute(query)

        await create_tables()

        consumer = AIOKafkaConsumer(
            *settings.TOPIC_NAMES,
            bootstrap_servers=settings.BOOTSTRAP_SERVERS,
            auto_offset_reset="earliest",
            group_id='consumer_for_clickhouse',
            enable_auto_commit=False,
        )

        await consumer.start()

        # Temporal storage for accumulating rows to make batch insert
        # into ClickHouse tables
        video_quality_change_clicks_batch_data = []
        video_pause_clicks_batch_data = []
        video_full_views_batch_data = []

        get_films_page_views_batch_data = []
        get_film_by_id_page_views_batch_data = []
        search_films_by_keyword_page_views_batch_data = []

        get_genres_page_views_batch_data = []
        get_genre_by_id_page_views_batch_data = []

        get_person_by_id_page_views_batch_data = []
        search_persons_by_keyword_page_views_batch_data = []

        while True:
            try:
                async for message in consumer:
                    if message.topic == settings.AsyncAPITopics.FILM_TOPIC.value:

                        if message.key.decode("utf-8") == settings.FilmTopicPartitions.GET_FILMS.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                get_films_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_get_films_page_views_table
                            )

                        elif message.key.decode("utf-8") == settings.FilmTopicPartitions.GET_FILM_BY_ID.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                get_film_by_id_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_get_film_by_id_page_views_table
                            )

                        elif message.key.decode("utf-8") == settings.FilmTopicPartitions.SEARCH_FILMS_BY_KEYWORD.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                search_films_by_keyword_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_search_films_by_keyword_page_views_table
                            )

                    elif message.topic == settings.AsyncAPITopics.GENRE_TOPIC.value:

                        if message.key.decode("utf-8") == settings.GenreTopicPartitions.GET_GENRES.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                get_genres_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_get_genres_page_views_table
                            )

                        elif message.key.decode("utf-8") == settings.GenreTopicPartitions.GET_GENRE_BY_ID.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                get_genre_by_id_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_get_genre_by_id_page_views_table
                            )

                    elif message.topic == settings.AsyncAPITopics.PERSON_TOPIC.value:

                        if message.key.decode("utf-8") == settings.PersonTopicPartitions.GET_PERSON_BY_ID.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                get_person_by_id_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_get_person_by_id_page_views_table
                            )

                        elif message.key.decode("utf-8") == settings.PersonTopicPartitions.SEARCH_PERSONS_BY_KEYWORD.value:
                            await load_data_to_clickhouse_from_async_api_kafka_topics(
                                message,
                                search_persons_by_keyword_page_views_batch_data,
                                consumer,
                                client,
                                queries.insert_into_search_persons_by_keyword_page_views_table
                            )

                    elif message.topic == settings.ClickTrackingTopics.QUALITY_CHANGE_CLICK.value:

                        await load_data_to_clickhouse_from_video_events_kafka_topics(
                            message,
                            video_quality_change_clicks_batch_data,
                            consumer,
                            client,
                            queries.insert_into_video_quality_change_clicks_table
                        )

                    elif message.topic == settings.ClickTrackingTopics.PAUSE_CLICK.value:

                        await load_data_to_clickhouse_from_video_events_kafka_topics(
                            message,
                            video_pause_clicks_batch_data,
                            consumer,
                            client,
                            queries.insert_into_video_pause_clicks_table
                        )

                    elif message.topic == settings.ClickTrackingTopics.FULL_VIEW.value:

                        await load_data_to_clickhouse_from_video_events_kafka_topics(
                            message,
                            video_full_views_batch_data,
                            consumer,
                            client,
                            queries.insert_into_video_full_views_table
                        )

            except KeyboardInterrupt:
                print("Exit using the keyboard")
            finally:
                await consumer.stop()


if __name__ == '__main__':
    asyncio.run(main())
