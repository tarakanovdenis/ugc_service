import asyncio

from redis import Redis

from core.config import settings
from services import rabbitmq
from db import redis


redis.redis = Redis(settings.redis_host, settings.redis_port)


if __name__ == '__main__':
    asyncio.run(rabbitmq.setup())
