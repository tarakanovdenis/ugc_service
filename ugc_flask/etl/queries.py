'''
Module has queries for creating ClickHouse database and tables
'''
from settings import (
    CLICKHOUSE_DATABASE_NAME,
    CLICKHOUSE_CLUSTER
)

# ClickHouse Table names
# Tables for Click Tracking Kafka Topic Messages
VIDEO_QUALITY_CHANGE_CLICKS = 'video_quality_change_clicks'
VIDEO_PAUSE_CLICKS = 'clicks_on_video_pauses'
VIDEO_FULL_VIEWS = 'clicks_on_video_full_views'

# Tables for AsyncAPI Service page views
# Film Enitity
GET_FILMS_PAGE_VIEWS = 'get_films_page_views'
GET_FILM_BY_ID_PAGE_VIEWS = 'get_film_by_id_page_views'
SEARCH_FILMS_BY_KEYWORD_PAGE_VIEWS = 'search_films_by_keyword_page_views'

# Genre Entitity
GET_GENRES_PAGE_VIEWS = 'get_genres_page_views'
GET_GENRE_BY_ID_PAGE_VIEWS = 'get_genre_by_id_page_views'

# Person Entitity
GET_PERSON_BY_ID_PAGE_VIEWS = 'get_person_by_id_page_views'
SEARCH_PERSONS_BY_KEYWORD_PAGE_VIEWS = 'search_persons_by_keyword_page_views'


drop_database = (
    f'''
    DROP DATABASE IF EXISTS {CLICKHOUSE_DATABASE_NAME}
    '''
)

create_database = (
    f'''
    CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}
    ON CLUSTER {CLICKHOUSE_CLUSTER}
    '''
)

# Video Quality Change Clicks Table
create_video_quality_change_clicks_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{VIDEO_QUALITY_CHANGE_CLICKS}
    (
        quality_before      String,
        quality_after       String,
        changed_at          Float32,
        timestamp           Int64
    )
    ENGINE = MergeTree()
    ORDER BY timestamp
    '''
)

insert_into_video_quality_change_clicks_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{VIDEO_QUALITY_CHANGE_CLICKS}
    (
        quality_before,
        quality_after,
        changed_at,
        timestamp
    )
    VALUES
    '''
)

select_from_video_quality_change_clicks_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{VIDEO_QUALITY_CHANGE_CLICKS}
    '''
)

# Video Pause Clicks Table

create_video_pause_clicks_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{VIDEO_PAUSE_CLICKS}
    (
        pause_at            Float32,
        timestamp           Int64
    )
    ENGINE = MergeTree()
    ORDER BY timestamp
    '''
)

insert_into_video_pause_clicks_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{VIDEO_PAUSE_CLICKS}
    (
        pause_at,
        timestamp
    )
    VALUES
    '''
)

select_from_video_pause_clicks_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{VIDEO_PAUSE_CLICKS}
    '''
)

# Video Full Views Table
create_video_full_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{VIDEO_FULL_VIEWS}
    (
        timestamp           Int64
    )
    ENGINE = MergeTree()
    ORDER BY timestamp
    '''
)

insert_into_video_full_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{VIDEO_FULL_VIEWS}
    (
        timestamp
    )
    VALUES
    '''
)

select_from_video_full_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{VIDEO_FULL_VIEWS}
    '''
)

# Get Films Page Views Table
create_get_films_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{GET_FILMS_PAGE_VIEWS}
    (
        user_id                     UUID,
        genre_query_param           String,
        sort_query_param            String,
        page_number_query_param     Int32,
        page_size_query_param       Int32,
        visited_at                  DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_get_films_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{GET_FILMS_PAGE_VIEWS}
    (
        user_id,
        genre_query_param,
        sort_query_param,
        page_number_query_param,
        page_size_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_get_films_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{GET_FILMS_PAGE_VIEWS}
    '''
)

# Get Film By ID Page Views Table
create_get_film_by_id_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{GET_FILM_BY_ID_PAGE_VIEWS}
    (
        user_id                 UUID,
        film_id_query_param     UUID,
        visited_at              DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_get_film_by_id_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{GET_FILM_BY_ID_PAGE_VIEWS}
    (
        user_id,
        film_id_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_get_film_by_id_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{GET_FILM_BY_ID_PAGE_VIEWS}
    '''
)

# Search Films By Keyword Page Views Table
create_search_films_by_keyword_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{SEARCH_FILMS_BY_KEYWORD_PAGE_VIEWS}
    (
        user_id                         UUID,
        keyword_to_search_query_param   String,
        genre_query_param               String,
        sort_query_param                String,
        page_number_query_param         Int32,
        page_size_query_param           Int32,
        visited_at                      DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_search_films_by_keyword_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{SEARCH_FILMS_BY_KEYWORD_PAGE_VIEWS}
    (
        user_id,
        keyword_to_search_query_param,
        genre_query_param,
        sort_query_param,
        page_number_query_param,
        page_size_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_search_films_by_keyword_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{SEARCH_FILMS_BY_KEYWORD_PAGE_VIEWS}
    '''
)

# Get Genres Page Views Table
create_get_genres_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{GET_GENRES_PAGE_VIEWS}
    (
        user_id                     UUID,
        page_number_query_param     Int32,
        page_size_query_param       Int32,
        visited_at                  DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_get_genres_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{GET_GENRES_PAGE_VIEWS}
    (
        user_id,
        page_number_query_param,
        page_size_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_get_genres_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{GET_GENRES_PAGE_VIEWS}
    '''
)

# Get Genre By ID Page Views Table
create_get_genre_by_id_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{GET_GENRE_BY_ID_PAGE_VIEWS}
    (
        user_id                 UUID,
        genre_id_query_param    UUID,
        visited_at              DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_get_genre_by_id_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{GET_GENRE_BY_ID_PAGE_VIEWS}
    (
        user_id,
        genre_id_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_get_genre_by_id_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{GET_GENRE_BY_ID_PAGE_VIEWS}
    '''
)

# Get Person By ID Page Views Table
create_get_person_by_id_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{GET_PERSON_BY_ID_PAGE_VIEWS}
    (
        user_id                 UUID,
        person_id_query_param   UUID,
        visited_at              DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_get_person_by_id_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{GET_PERSON_BY_ID_PAGE_VIEWS}
    (
        user_id,
        person_id_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_get_person_by_id_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{GET_PERSON_BY_ID_PAGE_VIEWS}
    '''
)

# Search Persons By Keyword Page Views Table
create_search_persons_by_keyword_page_views_table = (
    f'''
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DATABASE_NAME}.{SEARCH_PERSONS_BY_KEYWORD_PAGE_VIEWS}
    (
        user_id                         UUID,
        keyword_to_search_query_param   String,
        page_number_query_param         Int32,
        page_size_query_param           Int32,
        visited_at                      DateTime
    )
    ENGINE = MergeTree()
    ORDER BY user_id
    '''
)

insert_into_search_persons_by_keyword_page_views_table = (
    f'''
    INSERT INTO {CLICKHOUSE_DATABASE_NAME}.{SEARCH_PERSONS_BY_KEYWORD_PAGE_VIEWS}
    (
        user_id,
        keyword_to_search_query_param,
        page_number_query_param,
        page_size_query_param,
        visited_at
    )
    VALUES
    '''
)

select_from_search_persons_by_keyword_page_views_table = (
    f'''
    SELECT *
    FROM {CLICKHOUSE_DATABASE_NAME}.{SEARCH_PERSONS_BY_KEYWORD_PAGE_VIEWS}
    '''
)

table_creation_queries = [
    create_video_quality_change_clicks_table,
    create_video_pause_clicks_table,
    create_video_full_views_table,

    create_get_films_page_views_table,
    create_get_film_by_id_page_views_table,
    create_search_films_by_keyword_page_views_table,

    create_get_genres_page_views_table,
    create_get_genre_by_id_page_views_table,

    create_get_person_by_id_page_views_table,
    create_search_persons_by_keyword_page_views_table
]
