from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import BACK_BUTTON
from handlers.utils import try_send_message
from database.users import get_all_users_id
from filters.admin import IsAdmin


router = Router()


class SendMessageState(StatesGroup):
    choosing_message_to_send = State()


@router.callback_query(IsAdmin(),StateFilter(None), F.data == 'admin_send_message')
async def type_message_for_all_users(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    await try_send_message(callback,'Введи сообщение которое хочешь отправить пользователям: ', kb.as_markup())
    await state.set_state(SendMessageState.choosing_message_to_send)


@router.callback_query(IsAdmin(),F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    global CANCEL_BROADCAST
    await state.clear()
    CANCEL_BROADCAST = True
    await callback.answer("Рассылка будет остановлена!", reply_markup=kb.as_markup())


@router.message(SendMessageState.choosing_message_to_send)
async def send_message_to_all_users(message: Message):
    back_kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))

    global CANCEL_BROADCAST
    CANCEL_BROADCAST = False

    text_for_split = message.caption if message.photo else message.text
    if text_for_split is None:
        await message.answer("Нужно ввести текст в формате: текст@кнопка@ссылка")
        return

    msg = text_for_split.split('@')
    if len(msg) < 3:
        await message.answer("Неверный формат! Пример:\nТестовое сообщение@Купить@https://example.com\nПопробуй еще раз", reply_markup=back_kb.as_markup())
        return

    text, btn_text, btn_link = msg[0], msg[1], msg[2]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=btn_text, url=btn_link)]]
    )
    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⛔ Отменить рассылку", callback_data="cancel_broadcast")]
        ]
    )

    users = await get_all_users_id()
    total = len(users)
    sent = 0
    failed = 0
    photo_id = message.photo[-1].file_id if message.photo else None
    progress_msg = await message.answer(f"Начинаю рассылку...\n0% (0/{total})", reply_markup=cancel_kb)

    for i, user in enumerate(users, start=1):
        if CANCEL_BROADCAST:
            await progress_msg.edit_text(
                f"❗ Рассылка остановлена!\n"
                f"Отправлено: {sent}\n"
                f"Ошибок: {failed}",
            )

            await message.answer("Рассылка отменена.", reply_markup=back_kb.as_markup())
            return
        try:
            bot = message.bot
            if photo_id:
                await bot.send_photo(
                    chat_id=user,
                    photo=photo_id,
                    caption=text,
                    reply_markup=kb,
                )
            else:
                await bot.send_message(
                    chat_id=user,
                    text=text,
                    reply_markup=kb
                )
            sent += 1
        except:
            failed += 1

        if i % 10 == 0 or i == total:
            percent = int((i / total) * 100)
            try:
                await progress_msg.edit_text(
                    f"📤 Рассылка...\n"
                    f"Прогресс: {percent}% ({i}/{total})\n"
                    f"Успешно: {sent}\n"
                    f"Ошибок: {failed}",
                    reply_markup=cancel_kb
                )
            except:
                pass

    await progress_msg.edit_text(
        f"✅ Рассылка завершена!\n"
        f"Всего пользователей: {total}\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}"
    )

    await message.answer("Готово! Не болей родной <3", reply_markup=back_kb.as_markup())

