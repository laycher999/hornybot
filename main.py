import asyncio
from aiogram import Bot, Dispatcher

from handlers.middleware import LoggerAndAntiSpamMiddleware
from handlers import routers

from config import BOT_TOKEN

from database import create_table
from database.db import db
from database.media import clear_all_media

import redis.asyncio as redis
from aiogram.fsm.storage.redis import RedisStorage




bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    await db.connect()

    await create_table()

    for router in routers:
        dp.include_router(router)

    dp.callback_query.middleware(LoggerAndAntiSpamMiddleware(db))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
