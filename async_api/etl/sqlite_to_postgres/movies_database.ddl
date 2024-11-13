/*
АВТОР: Тараканов Денис
СОЗДАНО: 01.02.2024
E-MAIL: deniskatarakanov@yandex.ru
ОПИСАНИЕ: Данный DDL-файл содержит перечень SQL-запросов,
необходимых для создания базы данных о кинофильмах.
В базе данных в рамках схемы (content) будут созданы
пять таблиц: кинопроизведения (film_work), перечень жанров (genre),
участники кинопроизведения (person), связь кинопроизведений и участников
(person_film_work) и связь кинопроизведений и жанров (genre_film_work)
*/

-- Создаем схему content
CREATE SCHEMA IF NOT EXISTS content;

-- Создаем таблицу с информацией о кинофильмах
CREATE TABLE IF NOT EXISTS content.film_work (
	id UUID PRIMARY KEY,
	title TEXT NOT NULL,
	description TEXT NULL,
	creation_date DATE NULL,
	file_path TEXT NULL,
	rating FLOAT NULL,
	type TEXT NOT NULL,
	created TIMESTAMP WITH TIME ZONE,
	modified TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу с информацией о жанрах
CREATE TABLE IF NOT EXISTS content.genre (
	id UUID PRIMARY KEY,
	name TEXT NOT NULL,
	description TEXT NULL,
	created TIMESTAMP WITH TIME ZONE,
	modified TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу с информацией об участниках фильма
CREATE TABLE IF NOT EXISTS content.person (
	id UUID PRIMARY KEY,
	full_name TEXT NOT NULL,
	created TIMESTAMP WITH TIME ZONE,
	modified TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу, связывающую кинофильмы и их участников
CREATE TABLE IF NOT EXISTS content.person_film_work (
	id UUID PRIMARY KEY,
	person_id UUID NOT NULL,
	film_work_id UUID NOT NULL,
	role TEXT NOT NULL,
	created TIMESTAMP WITH TIME ZONE
);

-- Создаем таблицу, связывающую кинофильмы с их жанрами
CREATE TABLE IF NOT EXISTS content.genre_film_work (
	id UUID PRIMARY KEY,
    genre_id UUID NOT NULL,
	film_work_id UUID NOT NULL,
	created TIMESTAMP WITH TIME ZONE
);

-- Добавляем связь между записями таблиц film_work (id) и genre_film_work (film_work_id)
ALTER TABLE content.genre_film_work
ADD CONSTRAINT film_work_id_fk FOREIGN KEY (film_work_id)
REFERENCES content.film_work (id) DEFERRABLE INITIALLY DEFERRED;

-- Добавляем связь между записями таблиц genre (id) и genre_film_work (genre_id)
ALTER TABLE content.genre_film_work
ADD CONSTRAINT genre_id_fk FOREIGN KEY (genre_id)
REFERENCES content.genre (id) DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX genre_film_work_film_work_idx ON content.genre_film_work (film_work_id);
CREATE INDEX genre_film_work_genre_idx ON content.genre_film_work (genre_id);

-- Добавляем связь между записями таблиц film_work (id) и person_film_work (film_work_id)
ALTER TABLE content.person_film_work
ADD CONSTRAINT film_work_id_fk FOREIGN KEY (film_work_id)
REFERENCES content.film_work (id) DEFERRABLE INITIALLY DEFERRED;

-- Добавляем связь между записями таблиц person (id) и person_film_work (person_id)
ALTER TABLE content.person_film_work
ADD CONSTRAINT person_id_fk FOREIGN KEY (person_id)
REFERENCES content.person (id) DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX person_film_work_film_work_idx ON content.person_film_work (film_work_id);
CREATE INDEX person_film_work_person_idx ON content.person_film_work (person_id);

-- Создадим индекс для таблицы content.film_work для поля title
CREATE INDEX film_work_title_idx ON content.film_work (title);

-- Создадим композитный индекс для таблицы content.film_work для поля creation_date
-- поскольку дата создания часто используется при поиске фильмов
CREATE INDEX film_work_creation_date_rating_idx ON content.film_work (creation_date, rating);

-- Создаем индекс для таблицы content.person для поля full_name
CREATE INDEX person_full_name_idx ON content.person (full_name);

-- Создаем уникальный композитный индекс film_work_person_role_idx для таблицы
-- person_film_work, чтобы не было возможности добавить одного участника
-- c одной и той же ролью более одного раза к одному фильму
CREATE UNIQUE INDEX film_work_person_role_idx ON content.person_film_work (film_work_id, person_id, role);

-- Создаем уникальный композитный индекс film_work_genre_idx для таблицы genre_film_work,
-- чтобы не было возможности добавить один фильм более одного раза к одному и тому же жанру
CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);