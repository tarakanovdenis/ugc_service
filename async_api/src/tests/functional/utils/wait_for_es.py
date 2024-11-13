from elasticsearch import Elasticsearch

from src.tests.functional.settings import test_settings
from src.tests.functional.utils.backoff import backoff


es_client = Elasticsearch(
    hosts=[test_settings.es_host],
    verify_certs=False,
)


@backoff()
def check_connection_to_es():
    return es_client.ping()


if __name__ == '__main__':
    while True:
        if check_connection_to_es():
            break
