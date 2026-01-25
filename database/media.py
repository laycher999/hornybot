from database.db import db
from logger import logger



async def add_media(media_path: str, category:str, file_id: str):
    return await db.execute("INSERT INTO tg_media (media_path, category, file_id) VALUES ($1, $2, $3)",
                     media_path, category, file_id
                     )

async def get_media_id(media_path: str):
    row = await db.fetchval("SELECT file_id FROM tg_media WHERE media_path = $1", media_path)
    return row

async def clear_all_media():
    return await db.execute("TRUNCATE TABLE tg_media")

async def show_media_category():
    rows = await db.fetch("""
        SELECT category, COUNT(*) AS count
        FROM tg_media
        GROUP BY category
        ORDER BY category
    """)
    result = [ {"category": row["category"], "count": row["count"]} for row in rows ]
    return result

async def delete_media_category(category: str):
    return await db.execute("DELETE FROM tg_media WHERE category = $1", category)