import uuid
import pytest
from http import HTTPStatus

from src.tests.functional.settings import genre_test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'page_number': -1},
            {
                'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'msg': 'Input should be greater than or equal to 0'
            }
        ),
        (
            {'page_size': -1},
            {
                'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'msg': 'Input should be greater than or equal to 0'
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_genre_validation_error(
    es_write_data,
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    """Проверить валидацию данных запроса всех жанров."""

    es_data = [{
        'id': str(uuid.uuid4()),
        'name': 'Action',
        'description': 'The action film is a film genre which predominantly \
            features chase sequences, fights, shootouts, explosions, and \
            stunt work.'
    } for _ in range(50)]

    await es_write_data(
        genre_test_settings,
        es_data,
    )

    body, headers, status = await make_get_request(
        genre_test_settings.service_url + 'api/v1/genres/',
        params=query_data
    )

    assert status == expected_answer['status']
    assert body['detail'][0]['msg'] == expected_answer['msg']


@pytest.mark.asyncio
async def test_genre_list(
    es_write_data,
    make_get_request
):
    """Проверить вывод всех жанров."""

    es_data = [{
        'id': str(uuid.uuid4()),
        'name': 'Action',
        'description': 'The action film is a film genre which predominantly \
            features chase sequences, fights, shootouts, explosions, and \
            stunt work.'
    } for _ in range(3)]

    await es_write_data(
        genre_test_settings,
        es_data,
    )

    body, headers, status = await make_get_request(
        genre_test_settings.service_url + 'api/v1/genres/'
    )

    assert status == HTTPStatus.OK
    assert len(body) == 3


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            {
                'status': HTTPStatus.OK,
                'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
                'name': 'Action'
            }
        ),
        (
            'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
            {
                'status': HTTPStatus.OK,
                'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
                'name': 'Adventure'
            }
        ),
    ]
)
@pytest.mark.asyncio
async def test_genre_details(
    es_write_data,
    make_get_request,
    query_data: str,
    expected_answer: dict,
):
    """Проверить поиск конкретного жанра."""

    es_data = [
        {
            'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            'name': 'Action',
            'description': 'The action film is a film genre which predominantly \
                features chase sequences, fights, shootouts, explosions, and \
                stunt work.'
        },
        {
            'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
            'name': 'Adventure',
            'description': 'An adventure film is a form of adventure fiction, \
                and is a genre of film. Subgenres of adventure films include \
                swashbuckler films, pirate films, and survival films.'
        }
    ]

    await es_write_data(
        genre_test_settings,
        es_data
    )

    body, headers, status = await make_get_request(
        genre_test_settings.service_url + f'api/v1/genres/{query_data}'
    )

    assert status == expected_answer['status']
    assert body['id'] == expected_answer['id']
    assert body['name'] == expected_answer['name']


@pytest.mark.asyncio
async def test_redis_cache_genre_details(
    es_write_data,
    redis_client,
    make_get_request,
):
    """Проверить поиск конкретного жанра с учетом кэша Redis."""

    es_data = [
        {
            'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            'name': 'Action',
            'description': 'The action film is a film genre which predominantly \
                features chase sequences, fights, shootouts, explosions, and \
                stunt work.'
        },
    ]

    await es_write_data(
        genre_test_settings,
        es_data
    )

    await redis_client.flushdb(asynchronous=True)

    body, headers, status = await make_get_request(
        genre_test_settings.service_url + f'api/v1/genres/{es_data[0]["id"]}'
    )

    assert body['id'] == es_data[0]['id']
    assert body['name'] == es_data[0]['name']
    assert headers['X-Cache'] == 'MISS'

    body, headers, status = await make_get_request(
        genre_test_settings.service_url + f'api/v1/genres/{es_data[0]["id"]}'
    )

    assert body['id'] == es_data[0]['id']
    assert body['name'] == es_data[0]['name']
    assert headers['X-Cache'] == 'HIT'
    assert headers['Cache-Control'] == 'public, max-age=300'
