import pytest
import uuid
from http import HTTPStatus


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.CREATED,
                "title": "The Dark Knight",
                "description": "Some description about the film.",
                "id": str(uuid.uuid4()),
                "ratings": [],
                "reviews": [],
                "created_at": "2024-10-04T19:36:28.101Z"
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_film_create(
    get_authentication_token,
    make_post_request,
    expected_answer
):
    '''Check the creating the film.'''

    mongo_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film.",
        "id": str(uuid.uuid4()),
        "ratings": [],
        "reviews": [],
        "created_at": "2024-10-04T19:36:28.101Z"
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert status == expected_answer['status']
    assert body['title'] == expected_answer['title']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.OK,
                'film_number': 5
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_film_list(
    get_authentication_token,
    make_post_request,
    make_get_request,
    expected_answer
):
    '''Check the retrieving of all films.'''

    mongo_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film.",
        "id": str(uuid.uuid4()),
        "ratings": [],
        "reviews": [],
        "created_at": "2024-10-04T19:36:28.101Z"
    }

    access_token = await get_authentication_token()

    for _ in range(5):
        body, _, status = await make_post_request(
            'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
            json=mongo_data,
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

    body, _, status = await make_get_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['film_number']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.OK,
                "title": "The Dark Knight",
                "description": "Some description about the film.",
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_film_details(
    get_authentication_token,
    make_post_request,
    make_get_request,
    expected_answer
):
    '''Check the retrieving of the film details.'''

    mongo_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    body, _, status = await make_get_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/films/{body["id"]}',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert body['title'] == expected_answer['title']
    assert body['description'] == expected_answer['description']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.CREATED,
                "title": "Review on The Dark Knight",
                "body": "The review text.",
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_review_create(
    get_authentication_token,
    make_post_request,
    expected_answer
):
    '''Check the creating of the film review.'''

    mongo_film_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    mongo_review_data = {
        "title": "Review on The Dark Knight",
        "body": "The review text."
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_film_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/reviews/{body["id"]}',
        json=mongo_review_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert body['title'] == expected_answer['title']
    assert body['body'] == expected_answer['body']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.OK,
                "review_number": 5
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_get_review_by_film_id(
    get_authentication_token,
    make_post_request,
    make_get_request,
    expected_answer
):
    '''Check the retrieving of the film reviews.'''

    mongo_film_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    mongo_review_data = {
        "title": "Review on The Dark Knight",
        "body": "The review text.",
        'user_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_film_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    film_id = body['id']

    for _ in range(5):
        body, _, status = await make_post_request(
            'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/reviews/{film_id}',
            json=mongo_review_data,
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

    body, _, status = await make_get_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/reviews/{film_id}/films',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['review_number']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.CREATED,
                "rating": 7,
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_rating_create(
    get_authentication_token,
    make_post_request,
    expected_answer
):
    '''Check the creating of the film rating.'''

    mongo_film_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    mongo_rating_data = {
        "rating": 7,
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_film_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    film_id = body['id']

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/ratings/{film_id}',
        json=mongo_rating_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert body['rating'] == expected_answer['rating']
    assert body['film_id'] == film_id


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.OK,
                "rating_number": 5
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_get_rating_by_film_id(
    get_authentication_token,
    make_post_request,
    make_get_request,
    expected_answer
):
    '''Check the retrieving of the film ratings.'''

    mongo_film_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    mongo_rating_data = {
        "rating": 7,
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_film_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    film_id = body['id']

    for _ in range(5):
        body, _, status = await make_post_request(
            'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/ratings/{film_id}',
            json=mongo_rating_data,
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

    body, _, status = await make_get_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/ratings/{film_id}/films',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['rating_number']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.OK,
                "avg_rating_value": 9
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_get_avg_rating_value_by_film_id(
    get_authentication_token,
    make_post_request,
    make_get_request,
    expected_answer
):
    '''Check the retrieving of the film average rating value.'''

    mongo_film_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    mongo_rating_data = {
        "rating": 9,
    }

    access_token = await get_authentication_token()

    body, _, status = await make_post_request(
        'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
        json=mongo_film_data,
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    film_id = body['id']

    for _ in range(5):
        body, _, status = await make_post_request(
            'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/ratings/{film_id}',
            json=mongo_rating_data,
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

    body, _, status = await make_get_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/ratings/{film_id}/film',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert body['avg_rating_value'] == expected_answer['avg_rating_value']


@pytest.mark.parametrize(
    'expected_answer',
    [
        (
            {
                'status': HTTPStatus.OK,
                "film_number": 5,
            }
        )
    ]
)
@pytest.mark.asyncio
async def test_add_films_to_bookmark(
    get_authentication_token,
    make_post_request,
    make_get_request,
    expected_answer,
):
    '''Check the adding of the film to the user bookmark.'''

    mongo_film_data = {
        "title": "The Dark Knight",
        "description": "Some description about the film."
    }

    access_token = await get_authentication_token()

    for _ in range(5):
        body, _, status = await make_post_request(
            'http://backend_ugc_fastapi_for_test:8000' + '/ugc_fastapi/films/',
            json=mongo_film_data,
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

        film_id = body['id']

        body, _, status = await make_post_request(
            'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/bookmarks/{film_id}/films',
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

        user_id = body['user_id']

    body, _, status = await make_get_request(
        'http://backend_ugc_fastapi_for_test:8000' + f'/ugc_fastapi/bookmarks/{user_id}/users/films',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['film_number']
