from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, Response
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.models import Genre


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genres(
        self,
        page_number: int,
        page_size: int,
    ) -> Optional[list[Genre]]:
        body = {
            "from": page_number,
            "size": page_size,
        }
        genres = (await self.elastic.search(
            index='genres',
            body=body
        ))['hits']['hits']

        if genres:
            genre_list = [genre['_source'] for genre in genres]
            return genre_list
        return None

    async def get_genre_by_id(self, genre_id: str, response: Response) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id, response)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None

            await self._put_genre_to_cache(genre, response)

        return genre

    async def _get_genre_from_elastic(self, genre_id: str):
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None

        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str, response: Response) -> Optional[Genre]:
        data = await self.redis.get(f'genre_{genre_id}')
        if not data:
            return None

        response.headers['Cache-Control'] = 'public' + ', ' + f'max-age={GENRE_CACHE_EXPIRE_IN_SECONDS}'
        response.headers['X-Cache'] = 'HIT'

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre, response):
        await self.redis.set(
            f'genre_{genre.id}',
            genre.model_dump_json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS
        )
        response.headers['X-Cache'] = 'MISS'


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
