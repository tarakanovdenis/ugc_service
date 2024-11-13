from redis import Redis

from src.tests.functional.settings import test_settings
from src.tests.functional.utils.backoff import backoff


redis_client = Redis(
        host=test_settings.redis_host,
        port=test_settings.redis_port
)


@backoff()
def check_connection_to_redis():
    return redis_client.ping()


if __name__ == '__main__':
    while True:
        if check_connection_to_redis():
            break
