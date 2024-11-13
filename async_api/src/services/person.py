from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, Response
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.models import Person, Person_


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_person_by_id(self, person_id: str, response: Response) -> Optional[Person]:
        person = await self._person_from_cache(person_id, response)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None

            await self._put_person_to_cache(person, response)

        # Найти все фильмы, в которых принял участие person,
        # независимо от его роли
        person_films = (await self.elastic.search(
            index='movies',
            body={
                "from": 0,
                "size": 10,
                "query": {
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "actors",
                                    "query": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"actors.id": person.id}}
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "writers",
                                    "query": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"writers.id": person.id}}
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "directors",
                                    "query": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"directors.id": person.id}}
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            ))

        if not person_films:
            return None

        # Сгенерировать лист словарей-фильмов, в которых принял участие person
        person_dictionary_film_list = [
            person_film['_source'] for person_film in person_films['hits']['hits']
        ]

        # Получить json объект, включающий в себя id, full_name и список films,
        # состоящий из названий фильмов и ролей person в этих фильмах
        person_json = await self._get_film_with_roles_for_person(
            person_dictionary_film_list,
            person
        )

        return person_json

    async def search_persons(
        self,
        page_number: int,
        page_size: int,
        query: str = None,
    ) -> Optional[list[Person]]:
        if query:
            persons = (await self.elastic.search(
                index='persons',
                body={
                    "from": page_number,
                    "size": page_size,
                    "query": {
                        "match": {
                            "full_name": query,
                        }
                    }
                }
            ))
        else:
            persons = (await self.elastic.search(
                index='persons',
                body={
                    'from': page_number,
                    'size': page_size,
                    "query": {
                        "match_all": {}
                    }
                }
            ))

        if persons:

            person_list = []

            # Сгенерировать список словарей-персон, содержащих объекты Person_
            person_dictionary_list = [
                person['_source'] for person in persons['hits']['hits']
            ]
            for person in person_dictionary_list:
                # Найти фильмы по имени person, в которых он принял участие
                person_movies = (await self.elastic.search(
                    index='movies',
                    body={
                        "query": {
                            "multi_match": {
                                "query": person['full_name'],
                                "fields": [
                                    'actors_names',
                                    'directors_names',
                                    'writers_names'
                                ],
                                "operator": "AND"
                            }
                        }
                    }
                ))
                # Сгенерировать список словарей-фильмов, содержащих объекты
                # Film, в которых принял участие person
                person_movie_dictionary_list = [
                    movie['_source'] for movie in person_movies['hits']['hits']
                ]

                # Добавить json объект person, состоящий из id, full_name
                # и списка films, включающем название фильма и список roles -
                # ролей person в этом фильме
                person_list.append(
                    await self._get_film_with_roles_for_person(
                        person_movie_dictionary_list,
                        person
                    )
                )

            return person_list

        return None

    async def _get_film_with_roles_for_person(
        self,
        person_dictionary_film_list,
        person
    ):
        if isinstance(person, dict):
            person_json = {
                "id": person["id"],
                "full_name": person["full_name"],
                "films": []
            }
            # Проитерировать по каждому словарю-фильму, при этом проверив какую
            # роль имеет person в этом фильме и занося каждую роль в список roles
            for film in person_dictionary_film_list:
                roles = []

                if person['full_name'] in film['actors_names']:
                    roles.append('actor')
                if person['full_name'] in film['directors_names']:
                    roles.append('director')
                if person['full_name'] in film['writers_names']:
                    roles.append('writer')

                person_json['films'].append(
                        {
                            'id': film['id'],
                            'roles': roles
                        }
                    )

        else:
            person_json = {
                "id": person.id,
                "full_name": person.full_name,
                "films": []
            }
            # Проитерировать по каждому словарю-фильму, при этом проверив какую
            # роль имеет person в этом фильме и занося каждую роль в список roles
            for film in person_dictionary_film_list:
                roles = []

                if person.full_name in film['actors_names']:
                    roles.append('actor')
                if person.full_name in film['directors_names']:
                    roles.append('director')
                if person.full_name in film['writers_names']:
                    roles.append('writer')

            # Добавить в объект person_json объект словарь-фильм, состоящий
            # из названия фильма и ролей person в этом фильме
                person_json['films'].append(
                    {
                        'id': film['id'],
                        'roles': roles
                    }
                )

        return person_json

    async def _get_person_from_elastic(self, person_id: str):
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None

        return Person_(**doc['_source'])

    async def _person_from_cache(self, person_id: str, response: Response):
        data = await self.redis.get(f'person_{person_id}')
        if not data:
            return None

        response.headers['Cache-Control'] = 'public' + ', ' + f'max-age={PERSON_CACHE_EXPIRE_IN_SECONDS}'
        response.headers['X-Cache'] = 'HIT'

        person = Person_.parse_raw(data)

        return person

    async def _put_person_to_cache(self, person: Person_, response):
        await self.redis.set(
            f'person_{person.id}',
            person.model_dump_json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS
        )
        response.headers['X-Cache'] = 'MISS'


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
