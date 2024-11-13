import os
import unittest
from pathlib import Path

import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv


dotenv_path = Path('../../.env')
load_dotenv(dotenv_path=dotenv_path)

PATH_TO_SQLITE_DATABASE = 'sqlite_to_postgres/db.sqlite'


class TestDatabaseConsistency(unittest.TestCase):
    # Определяем метод 'setUp', выполняемый прежде других тестов
    def setUp(self):
        # Устанавливаем связь с базой данных (БД) SQLite
        self.sqlite_conn = sqlite3.connect(PATH_TO_SQLITE_DATABASE)
        self.sqlite_cursor = self.sqlite_conn.cursor()

        # Устанавливаем связь с БД PostgreSQL
        DSN = {
            'dbname': os.environ.get('POSTGRES_DB'),
            'user': os.environ.get('POSTGRES_USER'),
            'password': os.environ.get('POSTGRES_PASSWORD'),
            'host': os.environ.get('POSTGRES_HOST'),
            'port': os.environ.get('POSTGRES_PORT'),
        }

        self.pg_conn = psycopg2.connect(**DSN, cursor_factory=DictCursor)
        self.pg_cursor = self.pg_conn.cursor()

        # Определяем список названий таблиц как ожидаемый результат проверки
        # существущих таблиц в БД
        self.expected_table_names = [
            'genre',
            'genre_film_work',
            'person_film_work',
            'person',
            'film_work',
        ]

    # Определяем метод 'tearDown', выполняемый после других тестов
    def tearDown(self):
        # Закрываем соединения с БД
        self.sqlite_cursor.close()
        self.sqlite_conn.close()
        self.pg_cursor.close()
        self.pg_conn.close()

    # Определяем тест для проверки соответствия таблиц в БД
    def test_table_availability(self):
        '''
        Проверка соответствия таблиц (наличие и название) в базах данных
        '''
        # Выполняем запрос для получения всех имеющихся таблиц в БД SQLite
        # в виде списка названий таблиц
        self.sqlite_cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """)
        self.sqlite_available_tables = [
            table_name[0] for table_name in self.sqlite_cursor.fetchall()
        ]

        # Выполняем запрос для получения всех имеющихся таблиц в используемой
        # схеме 'content' в БД PostgreSQL в виде списка названий таблиц
        self.pg_cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'content'
        """)
        self.pg_available_tables = [
            table_name[0] for table_name in self.pg_cursor.fetchall()
        ]

        # Проверяем соответствие таблиц в БД SQLite
        self.assertCountEqual(
            self.sqlite_available_tables, self.expected_table_names
        )
        # Проверяем соответствие таблиц в БД PostgreSQL
        self.assertCountEqual(
            self.pg_available_tables, self.expected_table_names
        )

    # Определяем тест для проверки количества записей в каждой таблице
    def test_database_record_count(self):
        '''
        Проверка соответствия количества записей каждой таблицы в базах данных
        '''
        for table in self.expected_table_names:
            # Выполняем SQL запрос для выбора всех записей в таблице SQLite
            self.sqlite_cursor.execute(f"""
            SELECT * FROM {table}
            """)
            self.sqlite_results = self.sqlite_cursor.fetchall()

            # Выполняем SQL запрос для выбора всех записей в таблице PostgreSQL
            self.pg_cursor.execute(f"""
            SELECT * FROM content.{table}
            """)
            self.pg_results = self.pg_cursor.fetchall()

            self.assertEqual(len(self.sqlite_results), len(self.pg_results))

    # Определяем тест для проверки соответствия соодержимого в каждой таблице
    def test_database_content(self):
        '''
        Проверка соответствия содержимого каждой таблицы в базах данных
        '''
        for table in self.expected_table_names:
            # Выполняем SQL запрос для выбора всех записей в таблице SQLite
            self.sqlite_cursor.execute(f"""
            SELECT id FROM {table}
            """)
            self.sqlite_results = self.sqlite_cursor.fetchall()
            # Поскольку извлечение данных из SQLite возвращает список кортежей,
            # содержащих записи, переведем результат в список записей
            self.sqlite_results_list = [
                result[0] for result in self.sqlite_results
            ]

            # Выполняем SQL запрос для выбора всех записей в таблице PostgreSQL
            self.pg_cursor.execute(f"""
            SELECT id FROM content.{table}
            """)
            self.pg_results = self.pg_cursor.fetchall()
            # Поскольку извлечение данных из PostgreSQL возвращает список
            # списков, содержащих записи, переведем результат в список записей
            self.pg_results_list = [
                result[0] for result in self.pg_results
            ]

            self.assertCountEqual(
                self.sqlite_results_list,
                self.pg_results_list,
            )
