import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from src.tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=[test_settings.es_host],
        verify_certs=False
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(
        es_test_settings,
        data: list[dict],
    ):

        bulk_query: list[dict] = []
        for row in data:
            data = {
                '_index': f'{es_test_settings.es_index}',
                '_id': row['id']
            }
            data.update({'_source': row})
            bulk_query.append(data)

        if await es_client.indices.exists(index=es_test_settings.es_index):
            await es_client.indices.delete(index=es_test_settings.es_index)

        await es_client.indices.create(
            index=es_test_settings.es_index,
            mappings=es_test_settings.es_index_mappings,
            settings=es_test_settings.es_index_settings
        )

        updated, errors = await async_bulk(
            client=es_client,
            actions=bulk_query,
            refresh='wait_for'
        )

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner
