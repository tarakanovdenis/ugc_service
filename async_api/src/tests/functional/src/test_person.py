import uuid
import pytest
from http import HTTPStatus

from src.tests.functional.settings import person_test_settings, \
    movie_test_settings


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
async def test_person_validation_error(
    es_write_data,
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    """Проверить валидацию данных запроса всех персон."""

    es_data = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "Quentin Tarantino",
        } for _ in range(50)]

    await es_write_data(
        person_test_settings,
        es_data
    )

    body, headers, status = await make_get_request(
        person_test_settings.service_url + 'api/v1/persons/search',
        params=query_data
    )

    assert status == expected_answer['status']
    assert body['detail'][0]['msg'] == expected_answer['msg']


@pytest.mark.asyncio
async def test_person_list(
    es_write_data,
    make_get_request
):
    """Проверить вывод всех персон."""

    es_film_data = [
        {
            'id': '2a090dde-f688-46fe-a9f4-b781a985275e',
            'title': 'The Dark Knight',
            'description': 'Batman raises the stakes in the war on crime. \
                With the help of Lieutenant Jim Gordon and Prosecutor Harvey \
                Dent, he intends to clear the streets of Gotham of crime. \
                Cooperation turns out to be effective, but soon they will \
                find themselves in the midst of chaos unleashed by a rising \
                criminal genius known to the frightened townspeople as the Joker.',
            'imdb_rating': 9.0,
            'genre': [
                'Action',
                'Crime',
                'Drama'
            ],
            'actors': [
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
                    'name': 'Heath Ledger'
                },
                {
                    'id': '00395304-dd52-4c7b-be0d-c2cd7a495684',
                    'name': 'Christian Bale'
                }
            ],
            'actors_names': [
                'Heath Ledger',
                'Christian Bale'
            ],
            'directors': [
                {
                    'id': 'a1758395-9578-41af-88b8-3f9456e6d938',
                    'name': 'Christopher Nolan'
                }
            ],
            'directors_names': [
                'Christopher Nolan'
            ],
            'writers': [],
            'writers_names': [],
        }
    ]

    await es_write_data(
        movie_test_settings,
        es_film_data
    )

    es_person_data = [
        {
            'id': '00395304-dd52-4c7b-be0d-c2cd7a495684',
            'full_name': 'Christian Bale'
        },
        {
            'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            'full_name': 'Heath Ledger'
        },
        {
            'id': 'a1758395-9578-41af-88b8-3f9456e6d938',
            'full_name': 'Christopher Nolan'
        },
    ]

    await es_write_data(
        person_test_settings,
        es_person_data
    )

    body, headers, status = await make_get_request(
        person_test_settings.service_url + 'api/v1/persons/search',
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
                'full_name': 'Heath Ledger'
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_person_details(
    es_write_data,
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    """Проверить поиск конкретного персонажа."""

    es_film_data = [
        {
            'id': '2a090dde-f688-46fe-a9f4-b781a985275e',
            'title': 'The Dark Knight',
            'description': 'Batman raises the stakes in the war on crime. \
                With the help of Lieutenant Jim Gordon and Prosecutor Harvey \
                Dent, he intends to clear the streets of Gotham of crime. \
                Cooperation turns out to be effective, but soon they will \
                find themselves in the midst of chaos unleashed by a rising \
                criminal genius known to the frightened townspeople as the Joker.',
            'imdb_rating': 9.0,
            'genre': [
                'Action',
                'Crime',
                'Drama'
            ],
            'actors': [
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
                    'name': 'Heath Ledger'
                },
                {
                    'id': '00395304-dd52-4c7b-be0d-c2cd7a495684',
                    'name': 'Christian Bale'
                }
            ],
            'actors_names': [
                'Heath Ledger',
                'Christian Bale'
            ],
            'directors': [],
            'directors_names': [],
            'writers': [],
            'writers_names': [],
        }
    ]

    await es_write_data(
        movie_test_settings,
        es_film_data
    )

    es_person_data = [
        {
            'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            'full_name': 'Heath Ledger'
        }
    ]

    await es_write_data(
        person_test_settings,
        es_person_data
    )

    body, headers, status = await make_get_request(
        person_test_settings.service_url + f'api/v1/persons/{query_data}',
    )

    assert status == expected_answer['status']
    assert body['id'] == expected_answer['id']
    assert body['full_name'] == expected_answer['full_name']


@pytest.mark.asyncio
async def test_redis_cache_person_details(
    es_write_data,
    redis_client,
    make_get_request,
):
    """Проверить поиск конкретного персонажа с учетом кэша Redis."""

    es_film_data = [
        {
            'id': '2a090dde-f688-46fe-a9f4-b781a985275e',
            'title': 'The Dark Knight',
            'description': 'Batman raises the stakes in the war on crime. \
                With the help of Lieutenant Jim Gordon and Prosecutor Harvey \
                Dent, he intends to clear the streets of Gotham of crime. \
                Cooperation turns out to be effective, but soon they will \
                find themselves in the midst of chaos unleashed by a rising \
                criminal genius known to the frightened townspeople as the Joker.',
            'imdb_rating': 9.0,
            'genre': [
                'Action',
                'Crime',
                'Drama'
            ],
            'actors': [
                {
                    'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
                    'name': 'Heath Ledger'
                },
                {
                    'id': '00395304-dd52-4c7b-be0d-c2cd7a495684',
                    'name': 'Christian Bale'
                }
            ],
            'actors_names': [
                'Heath Ledger',
                'Christian Bale'
            ],
            'directors': [],
            'directors_names': [],
            'writers': [],
            'writers_names': [],
        }
    ]

    await es_write_data(
        movie_test_settings,
        es_film_data
    )

    es_person_data = [
        {
            'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            'full_name': 'Heath Ledger'
        }
    ]

    await es_write_data(
        person_test_settings,
        es_person_data,
    )

    await redis_client.flushdb(asynchronous=True)

    body, headers, status = await make_get_request(
        person_test_settings.service_url + f'api/v1/persons/{es_person_data[0]["id"]}'
    )

    assert body['id'] == es_person_data[0]['id']
    assert body['full_name'] == es_person_data[0]['full_name']
    assert headers['X-Cache'] == 'MISS'

    body, headers, status = await make_get_request(
        person_test_settings.service_url + f'api/v1/persons/{es_person_data[0]["id"]}'
    )

    assert body['id'] == es_person_data[0]['id']
    assert body['full_name'] == es_person_data[0]['full_name']
    assert headers['X-Cache'] == 'HIT'
    assert headers['Cache-Control'] == 'public, max-age=300'
