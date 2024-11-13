import time

from elasticsearch import Elasticsearch

from settings import settings


if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=settings.es_settings.elasticsearch_host,
        verify_certs=False
    )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
