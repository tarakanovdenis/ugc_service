import datetime
from uuid import uuid4
from dataclasses import dataclass


@dataclass
class FilmWork:
    id: uuid4
    title: str
    description: str
    creation_date: datetime.datetime
    file_path: str
    rating: float
    type: str
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class Genre:
    id: uuid4
    name: str
    description: str
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class Person:
    id: uuid4
    full_name: str
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class GenreFilmWork:
    id: uuid4
    film_work_id: uuid4
    genre_id: uuid4
    created: datetime.datetime


@dataclass
class PersonFilmWork:
    id: uuid4
    film_work_id: uuid4
    person_id: uuid4
    role: str
    created: datetime.datetime
