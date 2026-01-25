import time
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from datetime import datetime
from collections import defaultdict, deque

class LoggerAndAntiSpamMiddleware(BaseMiddleware):
    def __init__(self, db, limit=5, per=10):
        super().__init__()
        self.db = db
        self.limit = limit
        self.per = per
        self.clicks = defaultdict(deque)

    async def __call__(self, handler, event: CallbackQuery, data):
        user_id = event.from_user.id
        now = time.monotonic()
        queue = self.clicks[user_id]

        if isinstance(event, Message):
            text = event.text or event.caption or "<no text>"
            print(
                f"[LOG] user={event.from_user.id} "
                f"chat={event.chat.id} "
                f"text={text}"
            )

        while queue and queue[0] < now - self.per:
            queue.popleft()

        if len(queue) >= self.limit:
            await event.answer("🚫 Слишком много нажатий", show_alert=True)
            return

        queue.append(now)

        # СОХРАНЯЕМ В БАЗУ
        try:
            await self.db.execute(
                "UPDATE users SET last_seen=$1 WHERE user_id=$2",
                datetime.now(), event.from_user.id
            )
        except Exception as e:
            print("DB ERROR:", e)


        return await handler(event, data)
