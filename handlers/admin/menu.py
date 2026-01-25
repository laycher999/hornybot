from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery,  InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import BACK_BUTTON
from handlers.utils import try_send_message
from filters.admin import IsAdmin


router = Router()


@router.callback_query(IsAdmin(), F.data == 'admin_menu')
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='🔄 Перезагрузка', callback_data='admin_reload'))
    kb.add(InlineKeyboardButton(text='📊 Статистика', callback_data='admin_stats'))
    kb.row(InlineKeyboardButton(text='📤 Рассылка', callback_data='admin_send_message'))
    kb.row(InlineKeyboardButton(text='🎁 Призы', callback_data='admin_gifts_menu'))
    kb.row(InlineKeyboardButton(text='🗑️ Очистить фото-кэш', callback_data='admin_cache'))
    kb.adjust(3,1,1,1)
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))
    await try_send_message(callback,'admin menu', kb.as_markup())