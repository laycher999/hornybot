from database.db import db
from datetime import date, datetime

async def fill_cards():
    cards = {
        "Card12.mp4": "https://boosty.to/owandie/gift/97b13fa4-84b2-49f6-b9b4-67316a31683f/accept",
        "Card22.mp4": "https://boosty.to/owandie/gift/87d0fec0-f62b-4e9c-8016-12bb4e3aded0/accept",
        "Card32.mp4": "https://boosty.to/owandie/gift/831a3ed0-53a7-458a-a924-04295cc622cb/accept",
        "Card42.mp4": "https://boosty.to/owandie/gift/dcdc15a9-be90-45e8-abad-45f90a80444a/accept",
        "Card52.mp4": "https://boosty.to/owandie/gift/25797a30-9045-473e-88dc-10f5ce603f62/accept",
        "Card62.mp4": "https://boosty.to/owandie/gift/16b4f984-fe45-473f-a883-6806046f4859/accept",
        "Card72.mp4": "https://boosty.to/owandie/gift/c54aa630-8dc1-4c30-afc9-269072fec0ac/accept",
        "Card82.mp4": "https://boosty.to/owandie/gift/46123678-0523-4b20-beac-e38f4c64cd5e/accept",
        "Card92.mp4": "https://boosty.to/owandie/gift/00bbf17b-7794-4055-871f-bbb27d9e48ef/accept",
        "Card102.mp4": "https://boosty.to/owandie/gift/fa515cf2-e293-4e19-a7d8-8a2e6d39e902/accept"
    }
    query = """
    INSERT INTO cards (name, url)
    VALUES ($1, $2)
    """

    for name, url in cards.items():
        try:
            await db.execute(query, name, url)
        except:
            pass


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