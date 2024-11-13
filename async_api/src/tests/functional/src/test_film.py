import uuid
import pytest
from http import HTTPStatus
from src.tests.functional.settings import movie_test_settings


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
async def test_films_validation_error(
    es_write_data,
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    """Проверить валидацию данных запроса всех фильмов."""

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [
            'Action',
            'Sci-Fi'
        ],
        'title': 'The Star',
        'description': 'New World',
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'directors_names': ['Quentin', 'Christopher'],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ],
        'directors': [
            {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
            {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
        ]
    } for _ in range(10)]

    await es_write_data(
        movie_test_settings,
        es_data
    )

    body, headers, status = await make_get_request(
        movie_test_settings.service_url + 'api/v1/films/',
        params=query_data
    )

    assert status == expected_answer['status']
    assert body['detail'][0]['msg'] == expected_answer['msg']


@pytest.mark.asyncio
async def test_movie_list(
    es_write_data,
    make_get_request
):
    """Проверить вывод всех фильмов."""

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [
            'Action',
            'Sci-Fi'
        ],
        'title': 'The Star',
        'description': 'New World',
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'directors_names': ['Quentin', 'Christopher'],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ],
        'directors': [
            {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
            {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
        ]
    } for _ in range(10)]

    await es_write_data(
        movie_test_settings,
        es_data
    )

    body, headers, status = await make_get_request(
        movie_test_settings.service_url + 'api/v1/films'
    )

    assert status == HTTPStatus.OK
    assert len(body) == 10


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            {
                'status': HTTPStatus.OK,
                'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
                'imdb_rating': 8.5,
                'genre': [
                    'Action',
                    'Sci-Fi'
                ],
                'title': 'The Star',
                'description': 'New World',
                'actors_names': ['Ann', 'Bob'],
                'writers_names': ['Ben', 'Howard'],
                'directors_names': ['Quentin', 'Christopher'],
                'actors': [
                    {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                    {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
                ],
                'writers': [
                    {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                    {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
                ],
                'directors': [
                    {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
                    {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
                ]
            }
        ),
        (
            'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
            {
                'status': HTTPStatus.OK,
                'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
                'imdb_rating': 6.0,
                'genre': [
                    'Action',
                    'Sci-Fi'
                ],
                'title': 'Man',
                'description': 'New World',
                'actors_names': ['Ann', 'Bob'],
                'writers_names': ['Ben', 'Howard'],
                'directors_names': ['Quentin', 'Christopher'],
                'actors': [
                    {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                    {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
                ],
                'writers': [
                    {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                    {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
                ],
                'directors': [
                    {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
                    {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
                ]
            }
        ),
    ]
)
@pytest.mark.asyncio
async def test_movie_details(
    es_write_data,
    make_get_request,
    query_data: str,
    expected_answer: dict,
):
    """Проверить поиск конкретного фильма."""

    es_data = [
        {
            'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95',
            'imdb_rating': 8.5,
            'genre': [
                'Action',
                'Sci-Fi'
            ],
            'title': 'The Star',
            'description': 'New World',
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors_names': ['Quentin', 'Christopher'],
            'actors': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
            ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
            ],
            'directors': [
                {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
                {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
            ]
        },
        {
            'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
            'imdb_rating': 6.0,
            'genre': [
                'Action',
                'Sci-Fi'
            ],
            'title': 'Man',
            'description': 'New World',
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors_names': ['Quentin', 'Christopher'],
            'actors': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
            ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
            ],
            'directors': [
                {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
                {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
            ]
        }
    ]

    await es_write_data(
        movie_test_settings,
        es_data
    )

    body, headers, status = await make_get_request(
        movie_test_settings.service_url + f'api/v1/films/{query_data}'
    )

    assert status == expected_answer['status']
    assert body['id'] == expected_answer['id']
    assert body['title'] == expected_answer['title']


@pytest.mark.asyncio
async def test_redis_cache_movie_details(
    redis_client,
    es_write_data,
    make_get_request,
):
    """Проверить поиск конкретного фильма с учетом кэша Redis."""

    es_data = [
        {
            'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5',
            'imdb_rating': 6.0,
            'genre': [
                'Action',
                'Sci-Fi'
            ],
            'title': 'Man',
            'description': 'New World',
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors_names': ['Quentin', 'Christopher'],
            'actors': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
            ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
            ],
            'directors': [
                {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
                {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
            ]
        }
    ]

    await es_write_data(
        movie_test_settings,
        es_data
    )

    await redis_client.flushdb(asynchronous=True)

    body, headers, status = await make_get_request(
        movie_test_settings.service_url + f'api/v1/films/{es_data[0]["id"]}'
    )

    assert body['id'] == es_data[0]['id']
    assert body['title'] == es_data[0]['title']
    assert headers['X-Cache'] == 'MISS'

    body, headers, status = await make_get_request(
        movie_test_settings.service_url + f'api/v1/films/{es_data[0]["id"]}'
    )

    assert body['id'] == es_data[0]['id']
    assert body['title'] == es_data[0]['title']
    assert headers['X-Cache'] == 'HIT'
    assert headers['Cache-Control'] == 'public, max-age=300'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'The Star', 'page_size': 100},
            {'status': HTTPStatus.OK, 'length': 60}
        ),
        (
            {'query': 'Mashed Potato', 'page_size': 100},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_film_search(
    es_write_data,
    make_get_request,
    query_data: dict,
    expected_answer: dict
):
    """Проверить поиск фильмов по ключевым словам."""
    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [
            'Action',
            'Sci-Fi'
        ],
        'title': 'The Star',
        'description': 'New World',
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'directors_names': ['Quentin', 'Christopher'],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ],
        'directors': [
            {'id': '8c10ae99-80df-4dcb-929f-2f8dcf15f994', 'name': 'Quentin'},
            {'id': '97f168bd-d10d-481b-ad38-89d252a13feb', 'name': 'Christopher'}
        ]
    } for _ in range(60)]

    await es_write_data(
        movie_test_settings,
        es_data
    )

    body, headers, status = await make_get_request(
        movie_test_settings.service_url + 'api/v1/films/search',
        query_data
    )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']
