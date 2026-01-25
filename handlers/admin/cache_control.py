from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import BACK_BUTTON
from handlers.utils import try_send_message

from database.media import show_media_category, delete_media_category

router = Router()



@router.callback_query(F.data == 'admin_cache')
async def cache_control_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    media_category = await show_media_category()
    for item in media_category:
        text = f'{item['category']} ({item['count']})'
        kb.add(InlineKeyboardButton(text=text, callback_data='cache:clear:' + item['category']))
    kb.adjust(2)
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))
    await try_send_message(callback,'Category (file count)', kb.as_markup())


@router.callback_query(F.data.startswith('cache:clear'))
async def clear_cache_confirm(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='✅ Да', callback_data='confirm:'+callback.data))
    kb.add(InlineKeyboardButton(text='❌ Нет', callback_data='admin_cache'))
    category = callback.data.split(':')[-1]
    await try_send_message(callback,'⚠️ Вы точно хотите очистить файлы кеша в ' + category + '?', kb.as_markup())


@router.callback_query(F.data.startswith('confirm:cache:clear'))
async def clearing_cache(callback: CallbackQuery):
    category = callback.data.split(':')[-1]
    await callback.answer(category + " - была очищена!", show_alert=True)
    await delete_media_category(category)
    await cache_control_menu(callback)
