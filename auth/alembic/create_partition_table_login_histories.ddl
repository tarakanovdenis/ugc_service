/*
АВТОР: Тараканов Денис
СОЗДАНО: 18.08.2024
E-MAIL: deniskatarakanov@yandex.ru
ОПИСАНИЕ: Данный DDL-файл содержит перечень SQL-запросов,
необходимых для создания партицированных таблиц:
	- login_histories_console
	- login_histories_mobile
	- login_histories_tablet
	- login_histories_smarttv
	- login_histories_wearable
	- login_histories_embedded
	- login_histories_undefined
*/

CREATE TABLE IF NOT EXISTS login_histories_console
PARTITION OF login_histories
FOR VALUES IN ('console');

CREATE TABLE IF NOT EXISTS login_histories_mobile
PARTITION OF login_histories
FOR VALUES IN ('mobile');

CREATE TABLE IF NOT EXISTS login_histories_tablet
PARTITION OF login_histories
FOR VALUES IN ('tablet');

CREATE TABLE IF NOT EXISTS login_histories_smarttv
PARTITION OF login_histories
FOR VALUES IN ('smarttv');

CREATE TABLE IF NOT EXISTS login_histories_wearable
PARTITION OF login_histories
FOR VALUES IN ('wearable');

CREATE TABLE IF NOT EXISTS login_histories_embedded
PARTITION OF login_histories
FOR VALUES IN ('embedded');

CREATE TABLE IF NOT EXISTS login_histories_undefined
PARTITION OF login_histories
FOR VALUES IN ('undefined');