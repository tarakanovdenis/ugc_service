from __future__ import annotations
import json
import time
from datetime import datetime
from functools import wraps
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from aiokafka import AIOKafkaConsumer
    from aiokafka.structs import ConsumerRecord
    from aiochclient import ChClient


def backoff(
    start_sleep_time_sec=0.1,
    factor=2,
    border_sleep_time_sec=100,
):
    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            t = start_sleep_time_sec * (factor**2)
            while t < border_sleep_time_sec:
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    print(f"Waiting for a connection - {t}, sec.")
                    time.sleep(t)
                t = t * (factor**2)

        return inner

    return func_wrapper


@backoff()
async def load_data_to_clickhouse_from_async_api_kafka_topics(
    message: ConsumerRecord,
    temporal_storage: list,
    kafka_consumer: AIOKafkaConsumer,
    clickhouse_client: ChClient,
    insert_query: str,
    batch_size: int = 10,
):
    user_id, query_parameters, visited_at = tuple(
        json.loads(message.value.decode("utf-8")).values()
    )
    visited_at = datetime.strptime(visited_at, "%Y-%m-%d %H:%M:%S %z")
    temporal_storage.append(
        tuple([user_id, *query_parameters.values(), visited_at])
    )

    if len(temporal_storage) > batch_size:
        await clickhouse_client.execute(insert_query, *temporal_storage)
        await kafka_consumer.commit()
        temporal_storage.clear()


# @backoff()
async def load_data_to_clickhouse_from_video_events_kafka_topics(
    message: ConsumerRecord,
    temporal_storage: list,
    kafka_consumer: AIOKafkaConsumer,
    clickhouse_client: ChClient,
    insert_query: str,
    batch_size: int = 10,
):
    temporal_storage.append(
        tuple(json.loads(message.value.decode("utf-8")).values())
    )
    if len(temporal_storage) > batch_size:
        await clickhouse_client.execute(insert_query, *temporal_storage)
        await kafka_consumer.commit()
        temporal_storage.clear()
