from database.db import db
from datetime import date, datetime


async def can_play_today(user_id: int) -> bool:
    query = """
    SELECT created_at
    FROM user_items
    WHERE user_id = $1
    ORDER BY created_at DESC
    LIMIT 1
    """
    last_played = await db.fetchval(query, user_id)

    if last_played is None:
        return True

    return last_played.date() < date.today()

async def add_user_item(user_id, category, item_name):
    query = """
    INSERT INTO user_items (user_id, category, item_name)
    VALUES ($1, $2, $3)
    """
    await db.execute(query, user_id, category, item_name)

async def get_user_items(user_id: int):
    rows = await db.fetch(
        "SELECT id, item_name, category, created_at FROM user_items WHERE user_id=$1 ORDER BY created_at DESC",
        user_id
    )
    return [
        {
            "id": row['id'],
            "item_name": row['item_name'],
            "category": row['category'],
            "created_at": row['created_at'].strftime("%Y-%m-%d %H:%M:%S")  # строка
        }
        for row in rows
    ]

async def get_item_name(id: int):
    row = await db.fetchval("SELECT item_name FROM user_items WHERE id=$1", id)
    return row


async def get_all_user_items_category(user_id: int, category: str):
    query = """
    SELECT item_name FROM user_items WHERE user_id = $1 AND category = $2
    """
    row = await db.fetch(query, user_id, category)
    return [r['item_name'] for r in row]

async def score_category():
    query = """
    SELECT category, COUNT(*) AS total FROM user_items WHERE category IN 
    ('furry - 15%', 'futa - 5%', 'gay - 2.5%', 'lesbi - 2.5%', 'MEGAPRIZ - 0.25%', 'vpnAD - 5%', 'vpnWIN - 0.25%', 'straight') 
    GROUP BY category;
    """
    rows = await db.fetch(query)
    result = {row["category"]: row["total"] for row in rows}
    return result

async def show_most_active_users():
    query = """
    SELECT 
    i.user_id,
    u.first_name,
    COUNT(*) AS total
FROM user_items i
JOIN users u ON u.user_id = i.user_id
GROUP BY i.user_id, u.first_name
ORDER BY total DESC LIMIT 10;
    """
    rows = await db.fetch(query)
    result = [
        {
            'id': row['user_id'],
            'name': row['first_name'],
            'count': row['total']
        }
        for row in rows
    ]
    return result

async def show_user_place(user_id: int):
    query = """
SELECT place, total
FROM (
    SELECT 
        i.user_id,
        u.first_name,
        COUNT(*) AS total,
        RANK() OVER (ORDER BY COUNT(*) DESC) AS place
    FROM user_items i
    JOIN users u ON u.user_id = i.user_id
    GROUP BY i.user_id, u.first_name
) t
WHERE user_id = $1"""
    row =  await db.fetchrow(query, user_id)

    if row:
        result = (row['place'], row['total'])
    else:
        result = None
    return result