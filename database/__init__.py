from database.models import (
    create_users_to_games_table,
    create_users_table,
    create_user_items_table,
    create_media_table,
    create_users_favorite_games,
    create_gift_table
)

async def create_table():
    await create_users_table()
    await create_user_items_table()
    await create_users_to_games_table()
    await create_media_table()
    await create_users_favorite_games()
    await create_gift_table()

