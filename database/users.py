from database.db import db
from logger import logger
from datetime import datetime, date

async def add_user(user_id: int, user_name: str, last_name: str, first_name: str):
    row = await db.fetchrow("SELECT user_id FROM users WHERE user_id = $1", user_id)
    if row:
        return False

    query = """
        INSERT INTO users (user_id, nickname, first_name, last_name) 
        VALUES ($1, $2, $3, $4)
    """
    await db.execute(query, user_id, user_name, first_name, last_name)
    logger.info(f"Пользователь {user_name} зарегистрировался в базе данных.")


async def check_is_favorite(user_id: int, game_id: int):
    query = """
    SELECT user_id FROM users_to_games WHERE user_id = $1 AND game_id = $2
    """, user_id, game_id
    row = await db.fetchrow(*query)
    if row:
        return True
    else:
        return False


async def user_add_favorite_game(user_id: int, game_id: int):
    query = """
    INSERT INTO users_to_games (user_id, game_id) VALUES ($1,$2)
    """, user_id, game_id
    return await db.execute(*query)


async def user_remove_favorite_game(user_id: int, game_id: int):
    query = """
    DELETE FROM users_to_games WHERE user_id = $1 AND game_id = $2
    """, user_id, game_id
    return await db.execute(*query)


async def user_show_favorites_games(user_id: int):
    query = """
    SELECT game_id FROM users_to_games WHERE user_id = $1
    """
    rows = await db.fetch(query, user_id)
    if rows:
        return [row["game_id"] for row in rows]
    else:
        return False


async def get_all_users_id():
    query = """
    SELECT user_id FROM users
    """
    rows = await db.fetch(query)
    return [row['user_id'] for row in rows]


async def get_all_users_count():
    query = """
    SELECT COUNT(*) AS total
FROM users
"""
    row = await db.fetchrow(query)
    return row["total"]


async def get_active_users():
    query = """
    SELECT
    COUNT(*) FILTER (WHERE last_seen >= NOW() - INTERVAL '1 day') AS active_today,
    COUNT(*) FILTER (WHERE last_seen >= NOW() - INTERVAL '7 days') AS active_week,
    COUNT(*) FILTER (WHERE last_seen >= NOW() - INTERVAL '1 month') AS active_month
FROM users
    """
    row = await db.fetchrow(query)
    stats = {
        "active_today": row["active_today"],
        "active_week": row["active_week"],
        "active_month": row["active_month"]
    }
    return stats

async def get_all_users_favorite():
    query = """
    SELECT 
    COUNT(*) FROM users_to_games"""
    count = await db.fetchval(query)
    return count