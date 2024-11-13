import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class IdMixin(BaseModel):
    id: str

    class Config:
        model_validate_json = orjson.loads
        model_dump_json = orjson_dumps


class Person(IdMixin):
    full_name: str
    films: list[dict | None]


class Person_(IdMixin):
    full_name: str


class Actor(IdMixin):
    name: str


class Writer(IdMixin):
    name: str


class Director(IdMixin):
    name: str


class Film(IdMixin):
    title: str
    description: str | None
    imdb_rating: float | None
    actors: list[Actor]
    actors_names: list[str]
    directors: list[Director]
    directors_names: list[str]
    writers: list[Writer]
    writers_names: list[str]
    genre: list[str]


class Genre(IdMixin):
    name: str
    description: str | None
