from typing import Any

import psycopg2

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class Actor(Person):
    pass


class Writer(Person):
    pass


class Director(Person):
    pass


class FilmWork(BaseModel):
    id: str
    imdb_rating: float | None
    genre: list[str]
    title: str
    description: str | None
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[Actor]
    writers: list[Writer]
    directors: list[Director]


class Genre(BaseModel):
    id: str
    name: str
    description: str | None


class Person(BaseModel):
    id: str
    full_name: str


def transform_film_work_data(data: list[psycopg2.extras.DictRow]) -> list[str, Any]:
    '''
    Возвращает список отформатированных и валидированных записей фильмов.

        Параметры:
            data (list[psycopg2.extras.DictRow]): список обновленных записей
            фильмов

        Возвращаемое значение:
            validated_modified_film_works (list[str, Any]): список
            отформатированных и валидированных записей фильмов для
            загрузки в Elasticsearch
    '''

    validated_modified_film_works = [
        FilmWork(**_).model_dump() for _ in data
    ]
    return validated_modified_film_works


def transform_genre_data(data: list[psycopg2.extras.DictRow]) -> list[str, Any]:
    '''
    Возвращает список отформатированных и валидированных записей фильмов.

        Параметры:
            data (list[psycopg2.extras.DictRow]): список обновленных записей
            фильмов

        Возвращаемое значение:
            validated_modified_genre (list[str, Any]): список
            отформатированных и валидированных записей фильмов для
            загрузки в Elasticsearch
    '''

    validated_modified_genres = [
        Genre(**_).model_dump() for _ in data
    ]
    return validated_modified_genres


def transform_person_data(data: list[psycopg2.extras.DictRow]) -> list[str, Any]:
    '''
    Возвращает список отформатированных и валидированных записей фильмов.

        Параметры:
            data (list[psycopg2.extras.DictRow]): список обновленных записей
            фильмов

        Возвращаемое значение:
            validated_modified_genre (list[str, Any]): список
            отформатированных и валидированных записей фильмов для
            загрузки в Elasticsearch
    '''

    validated_modified_genres = [
        Person(**_).model_dump() for _ in data
    ]
    return validated_modified_genres
