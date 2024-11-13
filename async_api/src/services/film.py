from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, Response
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.models import Film


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films(
        self,
        genre: str,
        page_number: int,
        page_size: int,
        sort
    ) -> Optional[list[Film]]:
        if genre:
            films = (await self.elastic.search(
                index='movies',
                body={
                    "from": page_number,
                    "size": page_size,
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"genre": genre}}
                            ]
                        }
                    },
                    "sort": [{
                        "imdb_rating": sort
                    }],
                }
            ))['hits']['hits']
        else:
            films = (await self.elastic.search(
                    index='movies',
                    body={
                        "from": page_number,
                        "size": page_size,
                        "sort": [{
                            "imdb_rating": sort
                        }]
                    }
            ))['hits']['hits']
        if films:
            film_list = [film['_source'] for film in films]
            return film_list
        return None

    async def get_film_by_id(self, film_id: str, response: Response) -> Optional[Film]:
        film = await self._film_from_cache(film_id, response)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film, response)

        return film

    async def search_films(
        self,
        query: str,
        genre: str,
        page_number: int,
        page_size: int,
        sort
    ) -> Optional[list[Film]]:

        body = {
            "from": page_number,
            "size": page_size,
            "sort": [{
                "imdb_rating": sort
            }]

        }
        if query or genre:
            body['query'] = {'bool': {'must': []}}

        if query:
            body['query']['bool']["must"].append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title",
                            "description"
                        ],
                        "fuzziness": "AUTO"
                    }
                }
            )

        if genre:
            body['query']['bool']["must"].append(
                {
                    "match": {
                        "genre":
                            {
                                "query": genre,
                                "fuzziness": "AUTO"
                            }
                    }
                })

        films = (await self.elastic.search(
            index='movies',
            body=body
        ))['hits']['hits']

        if films:
            film_list = [film['_source'] for film in films]
            return film_list
        return None

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None

        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str, response: Response) -> Optional[Film]:
        data = await self.redis.get(f'movie_{film_id}')
        if not data:
            return None

        response.headers['Cache-Control'] = 'public' + ', ' + f'max-age={FILM_CACHE_EXPIRE_IN_SECONDS}'
        response.headers['X-Cache'] = 'HIT'

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film, response):
        await self.redis.set(
            f'movie_{film.id}',
            film.model_dump_json(),
            FILM_CACHE_EXPIRE_IN_SECONDS
        )
        response.headers['X-Cache'] = 'MISS'


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
