from aiogram import Router, F
from aiogram.types import CallbackQuery,  InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import os
from handlers.buttons import BACK_BUTTON
from handlers.utils import try_send_message


router = Router()



@router.callback_query(F.data == 'admin_reload')
async def admin_reload(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='✅ Да', callback_data='confirm:reload'))
    kb.add(InlineKeyboardButton(text='❌ Нет', callback_data='admin_menu'))
    await try_send_message(callback, '⚠️ Вы точно хотите перезагрузить бота?', kb.as_markup())


@router.callback_query(F.data == 'confirm:reload')
async def confirm_reload(callback: CallbackQuery):
    try:
        os.system("systemctl restart bot.service")
    except Exception as e:
        print(e)
    kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    await try_send_message(callback, '✅ Бот успешно перезагружен', kb.as_markup())

