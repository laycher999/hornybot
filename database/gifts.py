from database.db import db

async def add_gift(type: str, url: str):
    query = """
        INSERT INTO gifts (type, url) 
        VALUES ($1, $2)
    """
    await db.execute(query, type, url)


async def get_gift_and_remove(type: str):
    gift = await db.fetchrow("""
        DELETE FROM gifts
        WHERE id = (
            SELECT id
            FROM gifts
            WHERE type = $1
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING *;
    """, type)
    return gift

async def remove_gift(url):
    query = """
    DELETE FROM gifts WHERE url = $1"""
    await db.execute(query, url)

async def remove_gift_by_id(id):
    query = """
    DELETE FROM gifts WHERE id = $1"""
    await db.execute(query, id)

async def get_gifts(type: str):
    query = """
    SELECT id, url FROM gifts WHERE type = $1"""
    rows = await db.fetch(query, type)
    return [
        {
            "id": row['id'],
            "url": row['url'],
        }
        for row in rows
    ]