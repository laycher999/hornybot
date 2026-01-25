from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import os
from handlers.texts import GOTD_CATEGORIES_TO_EMOJI
from handlers.buttons import BACK_BUTTON
from handlers.utils import try_send_message
from database.users import get_active_users, get_all_users_count, get_all_users_favorite
from database.gotd import score_category

router = Router()


@router.callback_query(F.data == 'admin_stats')
async def admin_stats(callback: CallbackQuery):
    stats = await get_active_users()
    total_users = await get_all_users_count()
    users_favorite = await get_all_users_favorite()
    gotd_category_stats = await score_category()
    gotd_category_stats =  sorted(gotd_category_stats.items(), key=lambda x: x[1], reverse=True)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))

    text = f"""📊 Статистика проекта

👤 Пользователи:
├ 🗓️ За день: {stats['active_today']}
├ 📆 За неделю: {stats['active_week']}
├ 🗓️ За месяц: {stats['active_month']}
└ 🌐 Всего: {total_users}

🌸 Девочка-дня:
"""
    total_getted_items = 0
    for category, count in gotd_category_stats:
        text += f'├ {GOTD_CATEGORIES_TO_EMOJI.get(category)} {category.split('-')[0]}: {count}\n'
        total_getted_items += count
    text += f"""└ 🌐 Всего: {total_getted_items}

🌟 Добавлено в избранное: {users_favorite}
"""
    await try_send_message(callback, text, kb.as_markup())

class SendMessageState(StatesGroup):
    choosing_message_to_send = State()

