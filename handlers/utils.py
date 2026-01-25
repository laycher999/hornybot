import os
from aiogram.filters.callback_data import CallbackData
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    FSInputFile,
    InputMediaPhoto,
    InlineKeyboardButton, InputMediaVideo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from typing import Union
from database.media import add_media, get_media_id
from config import IMAGE_FORMATS, VIDEO_FORMATS
from .buttons import (
    PREV_PAGE,
    NEXT_PAGE,
    PREV_PAGE_X5,
    NEXT_PAGE_X5,
    FAVORITE_ADD,
    FAVORITE_DELETE,
)
from .texts import (
    FAVORITE_ADD_BUTTON_MSG,
    FAVORITE_DELETE_BUTTON_MSG
)
from database.users import (
    user_add_favorite_game,
    user_remove_favorite_game,
    check_is_favorite
)

router = Router()

async def split_list(lst, n):
    lst = [lst[i:i + n] for i in range(0, len(lst), n)]
    return lst

async def get_media_type(media_path):
    # Присваиваем переменной конец названия файла (формат файла)
    _, ext = os.path.splitext(media_path)
    media_type = 'video' if ext[1:] in VIDEO_FORMATS else 'photo'
    return media_type

async def try_send_message(
    target: Union[Message, CallbackQuery],
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    media_path: str | None = None,
    parse_mode: str = 'HTML'
):
    message: Message = (target.message if isinstance(target, CallbackQuery) else target)
    media = None
    media_type = None

    if media_path:
        media_type = await get_media_type(media_path)
        category = media_path.split('/')[2] if '.' not in media_path.split('/')[2] else 'other'

        # Попытка получить file_id из базы
        media = await get_media_id(media_path)

        if media is None:
            # Если нет file_id, загружаем фото на сервер Telegram
            fs_media = FSInputFile(media_path)

            if media_type == 'photo':
                try:
                    sent_msg = await message.answer_photo(photo=fs_media, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
                except TelegramBadRequest:
                    sent_msg = await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
                # Получаем file_id и сохраняем в базу
                file_id = sent_msg.photo[-1].file_id
                await add_media(media_path, category, file_id)
                return
            if media_type == 'video':
                try:
                    sent_msg = await message.answer_video(video=fs_media, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
                except TelegramBadRequest:
                    sent_msg = await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
                # Получаем file_id и сохраняем в базу
                file_id = sent_msg.video.file_id
                await add_media(media_path, category, file_id)
                return

    # Если file_id - True, редактируем сообщение или отправляем заново
    try:
        if media:
            if media_type == 'photo':
                await message.edit_media(
                    media=InputMediaPhoto(media=media, caption=text,parse_mode=parse_mode),
                       reply_markup=reply_markup
                )
            if media_type == 'video':
                await message.edit_media(
                    media=InputMediaVideo(media=media, caption=text,parse_mode=parse_mode),
                    reply_markup=reply_markup
                )
        else:
            await message.edit_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)

    except TelegramBadRequest:
        if media:
            if media_type == 'photo':
                await message.answer_photo(photo=media, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            if media_type == 'video':
                await message.answer_video(video=media, caption=text, reply_markup=reply_markup,parse_mode=parse_mode)
        else:
            await message.delete()
            await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)

class PageCallback(CallbackData, prefix='page'):
    page: int
    menu: str

async def page_menu(page_number: int, total_page: int, menu: str):
    kb = InlineKeyboardBuilder()


    kb.add(InlineKeyboardButton(text=PREV_PAGE_X5, callback_data=PageCallback(page=page_number-5, menu=menu).pack()))
    kb.add(InlineKeyboardButton(text=PREV_PAGE, callback_data=PageCallback(page=page_number-1, menu=menu).pack()))

    kb.add(InlineKeyboardButton(text=f'{page_number+1}/{total_page}', callback_data="ignore"))

    kb.add(InlineKeyboardButton(text=NEXT_PAGE, callback_data=PageCallback(page=page_number+1, menu=menu).pack()))
    kb.add(InlineKeyboardButton(text=NEXT_PAGE_X5, callback_data=PageCallback(page=page_number+5, menu=menu).pack()))

    return kb


class FavoriteCallback(CallbackData, prefix='favorite'):
    action: str
    game_id: int


@router.callback_query(FavoriteCallback.filter())
async def delete_or_add_to_favorite(callback: CallbackQuery, callback_data: FavoriteCallback):
    action = callback_data.action
    game_id = callback_data.game_id
    user_id = callback.from_user.id
    if action == 'add':
        await user_add_favorite_game(user_id, game_id)
        await callback.answer(FAVORITE_ADD_BUTTON_MSG, show_alert=True)

    if action == 'delete':
        await user_remove_favorite_game(user_id, game_id)
        await callback.answer(FAVORITE_DELETE_BUTTON_MSG, show_alert=True)


async def favorite_button(user_id: int, game_id: int):
    is_favorite = await check_is_favorite(user_id, game_id)
    if is_favorite:
        button = InlineKeyboardButton(text=FAVORITE_DELETE,
                                      callback_data=FavoriteCallback(action='delete', game_id=game_id).pack())
    else:
        button = InlineKeyboardButton(text=FAVORITE_ADD,
                                      callback_data=FavoriteCallback(action='add',game_id=game_id).pack())
    return button

