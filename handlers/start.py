from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logger import logger
from handlers.texts import (
    START_WELCOME_MESSAGE
)
from handlers.buttons import (
    START_BTNS,
    ADMIN_BTN,
)
from config import ADMINS
from database.users import add_user
from .utils import try_send_message, PageCallback

router = Router()

@router.callback_query(F.data == "start")
@router.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=START_BTNS[5], callback_data='casino_user_menu'))
    kb.row(InlineKeyboardButton(text=START_BTNS[2], callback_data=PageCallback(page=0, menu='my_translates').pack()))
    kb.row(InlineKeyboardButton(text=START_BTNS[6], url='https://t.me/hornystore_bot'))
    kb.row(InlineKeyboardButton(text=START_BTNS[1], callback_data='find_game'))
    kb.add(InlineKeyboardButton(text=START_BTNS[0], callback_data='quiz_menu'))
    kb.row(InlineKeyboardButton(text=START_BTNS[4], callback_data='my_favorites'))
    kb.add(InlineKeyboardButton(text=START_BTNS[3], callback_data=PageCallback(page=0, menu='poleznosti').pack())) 
    
    if message.from_user.id in ADMINS:
        kb.row(InlineKeyboardButton(text=ADMIN_BTN, callback_data='admin_menu'))

    await add_user(message.from_user.id, message.from_user.username,
                   message.from_user.last_name, message.from_user.first_name)

    photo = "./img/start.jpeg"
    await try_send_message(message, START_WELCOME_MESSAGE, kb.as_markup(), photo)



