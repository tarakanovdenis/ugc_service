import os
import sqlite3
import unittest
from contextlib import closing
from dataclasses import fields, astuple
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

from dataclasses_for_load_data import (
    FilmWork,
    Genre,
    Person,
    GenreFilmWork,
    PersonFilmWork,
)
from tests.check_consistency import *


dotenv_path = Path(__file__).parent.parent

load_dotenv(dotenv_path=dotenv_path)

PATH_TO_SQLITE_DATABASE = 'sqlite_to_postgres/db.sqlite'

# Создаем словарь, содержащий названия таблиц в базах данных (БД)
# и соответствующие им датаклассы
TABLE_SCHEMAS = {
    'film_work': FilmWork,
    'genre': Genre,
    'genre_film_work': GenreFilmWork,
    'person': Person,
    'person_film_work': PersonFilmWork,
}


def save_data_from_sqlite_to_postgres(
        sqlite_cursor, pg_cursor, table_name: str
):
    """Извлекает данные из SQLite и переносит их в PostgreSQL"""
    # Удаляем все записи в таблице, чтобы избежать дублирования записей
    # pg_cursor.execute(f"""TRUNCATE content.{table_name}""")
    # table_name = 'genre'
    # Извлекаем данные из таблицы БД SQLite
    sqlite_cursor.execute(f"""SELECT * FROM {table_name}""")

    # Определяем размер части для выгрузки данных из БД SQLite
    batch_size = 250

    # Извлекаем данные из таблицы SQLite в таблицу PostgreSQL по частям
    while True:
        results = sqlite_cursor.fetchmany(batch_size)
        if not results:
            break

        # Создаем экзепляр датакласса, соответствующего таблице
        table_row = TABLE_SCHEMAS[table_name](**results[0])

        # Получаем названия колонок таблицы (полей датакласса)
        column_names = [field.name for field in fields(table_row)]
        column_names_str = ','.join(column_names)

        # В зависимости от количества колонок генерируем под них %s
        col_count = ', '.join(['%s'] * len(column_names))

        # Создаем лист, содержащий все записи таблицы
        table_rows = [TABLE_SCHEMAS[table_name](**_) for _ in results]

        # Генерируем часть VALUES команды INSERT
        bind_values = ','.join(
            pg_cursor.mogrify(
                f'({col_count})', astuple(row)
                ).decode('utf-8') for row in table_rows
            )

        # Проводим вставку данных в соответствующую таблицу БД PostgreSQL
        pg_cursor.execute(f"""
        INSERT INTO content.{table_name} ({column_names_str})
        VALUES {bind_values}
        ON CONFLICT (id) DO NOTHING
        """)


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    sqlite_conn.row_factory = sqlite3.Row
    with closing(sqlite_conn.cursor()) as sqlite_cursor, \
            pg_conn.cursor() as pg_cursor:
        # Извлекаем набор таблиц из базы данных SQLite (db.sqlite)
        sqlite_cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """)
        # Получаем список названий таблиц в виде одиночных кортежей:
        # [('table_name_1'), ('table_name_2'), ...]
        sqlite_table_names = sqlite_cursor.fetchall()
        # Получаем отсортированный список названий таблиц в виде строк
        sqlite_table_names_list = sorted(
            [table_name[0] for table_name in sqlite_table_names]
        )

        # Извлекаем набор таблиц из базы данных PostgreSQL (movies_database)
        pg_cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'content'
        """)
        # Получаем список названий таблиц в виде одиночных кортежей:
        # [('table_name_1'), ('table_name_2'), ...]
        pg_table_names = pg_cursor.fetchall()
        # Получаем отсортированный список названий таблиц в виде строк
        pg_table_names_list = sorted(
            [table_name[0] for table_name in pg_table_names]
        )

        # Проверяем соответствие количества и названий таблиц в базах данных
        if len(sqlite_table_names_list) != len(pg_table_names_list):
            raise Exception('Количество таблиц в базах данных не совпадает.')
        elif sqlite_table_names_list != pg_table_names_list:
            raise Exception('Названия таблиц в базах данных неидентичны.')

        # Переносим данные из базы данных SQLite в базу данных PostgreSQL
        for table in sqlite_table_names_list:
            save_data_from_sqlite_to_postgres(sqlite_cursor, pg_cursor, table)


if __name__ == '__main__':
    DSN = {
        'dbname': os.environ.get('POSTGRES_DB'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('POSTGRES_HOST'),
        'port': os.environ.get('POSTGRES_PORT'),
    }

    with closing(sqlite3.connect(PATH_TO_SQLITE_DATABASE)) as sqlite_conn, \
            psycopg2.connect(**DSN, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)

    unittest.main(verbosity=3)
