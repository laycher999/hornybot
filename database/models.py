from database.db import db

async def create_users_table():
    query = """
       CREATE TABLE IF NOT EXISTS users
       (
           user_id BIGSERIAL PRIMARY KEY,
           nickname TEXT,
           first_name TEXT,
           last_name TEXT,
           last_seen DATE
       )
       """
    return await db.execute(query)


async def create_users_to_games_table():
    query = """
       CREATE TABLE IF NOT EXISTS users_to_games
       (
           user_id BIGINT NOT NULL,
           game_id INTEGER
       )
       """
    return await db.execute(query)


async def create_user_items_table():
    query = """
       CREATE TABLE IF NOT EXISTS user_items
       (
           id SERIAL PRIMARY KEY,
           user_id BIGINT NOT NULL,
           category VARCHAR(100) NOT NULL,
           item_name VARCHAR(255) NOT NULL,
           created_at TIMESTAMP DEFAULT NOW()
       )
       """
    return await db.execute(query)

async def create_media_table():
    query = """
    CREATE TABLE IF NOT EXISTS tg_media
    (
        id SERIAL PRIMARY KEY,
        media_path TEXT UNIQUE NOT NULL,
        category VARCHAR(100) NOT NULL,
        file_id TEXT NOT NULL
    )
    """
    return await db.execute(query)


async def create_users_favorite_games():
    query = """
    CREATE TABLE IF NOT EXISTS users_to_games
    (
    user_id BIGINT NOT NULL,
    game_id INTEGER
    )
    """
    return await db.execute(query)

async def create_gift_table():
    query = """
    CREATE TABLE IF NOT EXISTS gifts (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE
    )
    """
    await db.execute(query)



