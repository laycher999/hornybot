from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asyncio import sleep
import random
import os
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .buttons import (
    BACK_BUTTON
)
from config import ADMINS
from database.gifts import get_gift_and_remove
from database.gotd import can_play_today, get_user_items, add_user_item, get_item_name, get_all_user_items_category, show_most_active_users, show_user_place
from .texts import NEGATIVE_REACTIONS, POSITIVE_REACTIONS, GOTD_ALREADY_PLAYED_MSG, TEXT_TO_FOLDER, GOTD_FIRST_MENU_MSG, \
    GOTD_NOMEGAPRIZ_TEXT, GOTD_CATEGORIES_TO_EMOJI, GOTD_NO_ITEMS_MSG, GOTD_HISTORY_PAGEMENU_MSG, GOTD_HISTORY_ITEM_MSG, GOTD_LOADING_MESSAGES
from .buttons import GOTD_GET_GIRL_BTN, GOTD_HISTORY_BTN, GOTD_MEGAPRIZ_BTN, GOTD_VPNWIN_BTN, GOTD_VPNAD_BTN
from .utils import try_send_message, page_menu, PageCallback, split_list

router = Router()

IMAGE_FOLDERS = {
"furry - 15%": 10,
"futa - 5%": 3,
 "gay - 2.5%": 1.5,
 "lesbi - 2.5%": 1.5,
 "MEGAPRIZ - 0.25%": 0.25,
 "vpnAD - 5%": 5,
 "vpnWIN - 0.25%": 0.25,
"straight": 100
}


total_specified = sum([v for k, v in IMAGE_FOLDERS.items() if k != "straight"])
IMAGE_FOLDERS["straight"] = 100 - total_specified

async def choose_folder():
    chance = random.uniform(0, 100)
    current = 0
    for folder, prob in IMAGE_FOLDERS.items():
        current += prob
        if chance <= current:
            return folder
    return "straight"

async def get_random_image(folder, user_id):
    if folder.split('-')[0] in ["futa", "fury", "gay", "lesbi", "straight"]:
        user_items = await get_all_user_items_category(user_id, folder)
    else:
        user_items = None

    path = os.path.join("./img/casino_files", folder)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f not in user_items]
    if not files:
        return None
    return os.path.join(path, random.choice(files))


@router.callback_query(F.data == 'casino_user_menu')
async def casino_menu(callback: types.CallbackQuery):
    btns = [
        [types.InlineKeyboardButton(text=GOTD_GET_GIRL_BTN, callback_data='get_item')],
        [types.InlineKeyboardButton(text=GOTD_HISTORY_BTN, callback_data='item_history')],
        [types.InlineKeyboardButton(text="Top 10 collectors", callback_data='gotd_leaderboard')],

        [types.InlineKeyboardButton(text=BACK_BUTTON, callback_data='start')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)
    await try_send_message(target=callback, text=GOTD_FIRST_MENU_MSG, reply_markup=keyboard)

@router.callback_query(F.data == 'get_item')
async def casino_start_validating(callback: types.CallbackQuery):
    if not await can_play_today(callback.from_user.id):
        text = GOTD_ALREADY_PLAYED_MSG
        btns = [
             [types.InlineKeyboardButton(text=random.choice(NEGATIVE_REACTIONS), callback_data='casino_user_menu')]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)
        await try_send_message(target=callback,text=text, reply_markup=keyboard)
        return
    rand = random.randint(0, len(GOTD_LOADING_MESSAGES) - 1)
    msg = GOTD_LOADING_MESSAGES[rand]
    await try_send_message(target=callback, text=msg)
    await sleep(2)
    await casino_start(callback)

async def casino_start(callback: types.CallbackQuery):
    try:
        btns = [ [types.InlineKeyboardButton(text=random.choice(POSITIVE_REACTIONS), callback_data='casino_user_menu')]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)


        #Получение папки, файла и обработка случая если закончатся картинки
        folder = await choose_folder()
        media_path = await get_random_image(folder, callback.from_user.id)
        if media_path is None:
            await try_send_message(callback, 'Для вас у нас закончились девочки =(', reply_markup=keyboard)

        text = TEXT_TO_FOLDER[folder]

        await add_user_item(callback.from_user.id, folder, media_path)
        if folder in ['MEGAPRIZ - 0.25%', 'vpnWIN - 0.25%']:
            text = f"{folder.split('-')[0]} выпал пользователю @{callback.from_user.username}"
            for admin_id in ADMINS:
                await callback.message.bot.send_message(admin_id, text)

        if folder == 'MEGAPRIZ - 0.25%':
            try:
                url = await get_gift_and_remove('boosty')
                btns.append([types.InlineKeyboardButton(text=GOTD_MEGAPRIZ_BTN, url=url)])
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)
                video = f'./img/casino_files/MEGAPRIZ - 0.25%/Card102.mp4'
                await try_send_message(target=callback, text=text, media_path=video, reply_markup=keyboard)
            except:
                await try_send_message(target=callback, text=GOTD_NOMEGAPRIZ_TEXT, reply_markup=keyboard)
        else:
            if folder == "vpnAD - 5%":
                btns.append([types.InlineKeyboardButton(text=GOTD_VPNAD_BTN, url='https://t.me/@hornystore_bot')])
            elif folder == "vpnWIN - 0.25%":
                url = await get_gift_and_remove('vpn')
                btns.append([types.InlineKeyboardButton(text=GOTD_VPNWIN_BTN, url=url)])
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=btns)
            await try_send_message(target=callback, text=text, media_path=media_path, reply_markup=keyboard)
    except Exception as e:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=
                                              [types.InlineKeyboardButton(text='Назад', callback_data='casino_user_menu')]
                                              )
        await try_send_message(target=callback, text='Что-то пошло не так. Попробуйте еще раз', reply_markup=keyboard)
        for admin_id in ADMINS:
            await callback.message.bot.send_message(admin_id, 'Ошибка при получение девочки:\n' + e)


class ItemsHistory(StatesGroup):
    items_list = State()

@router.callback_query(F.data == 'item_history')
async def casino_history(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ItemsHistory.items_list)

    user_id = callback.from_user.id
    images = await get_user_items(user_id)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='casino_user_menu'))
    if not images:
        await try_send_message(callback, GOTD_NO_ITEMS_MSG, kb.as_markup())
        return

    await state.update_data(items_list=images)
    await gotd_history_pagemenu(callback, state, PageCallback(page=0, menu='gotd_history_pagemenu'))


@router.callback_query(PageCallback.filter(F.menu == 'gotd_history_pagemenu'))
async def gotd_history_pagemenu(callback: types.CallbackQuery, state: FSMContext, callback_data: PageCallback):
    data = await state.get_data()
    items_list = data['items_list']
    number_of_items = len(items_list)
    items_list = await split_list(items_list, 12)
    page_number = max(0, min(callback_data.page, len(items_list) - 1))
    kb = await page_menu(page_number, len(items_list), 'gotd_history_pagemenu')

    for i, item in enumerate(items_list[page_number]):
        category = item['category']
        emoji = GOTD_CATEGORIES_TO_EMOJI.get(category)
        created_at = item['created_at']
        id = item['id']
        kb.row(InlineKeyboardButton(text=f'{emoji} {created_at}', callback_data=f'gotd:item:{id}'))

    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='casino_user_menu'))

    await try_send_message(callback, GOTD_HISTORY_PAGEMENU_MSG.format(number_of_items=number_of_items), kb.as_markup())


@router.callback_query(F.data.startswith('gotd:item'))
async def show_selected_item(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data=PageCallback(page=0, menu='gotd_history_pagemenu').pack()))
    item_id = int(callback.data.split(':')[-1])
    item_name = await get_item_name(item_id)
    await try_send_message(callback, GOTD_HISTORY_ITEM_MSG.format(item_id=item_id), kb.as_markup(), item_name)


@router.callback_query(F.data == 'gotd_leaderboard')
async def show_leaderboard(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    user_in_top10 = False

    leaderboard = await show_most_active_users()
    for i, user in enumerate(leaderboard):
        id, name, count = user['id'], user['name'], user['count']
        text = f'{i+1}. {name} - 👧{count}'
        if id == callback.from_user.id:
                text += '   ⬅️ ВЫ'
                user_in_top10 = True
        kb.row(InlineKeyboardButton(text=text, callback_data='None'))

    if not user_in_top10:
        result = await show_user_place(callback.from_user.id)
        if result:
            place, count = result
            text = f'{place}. {callback.from_user.first_name} - 👧{count}  ⬅️ ВЫ'
            kb.row(InlineKeyboardButton(text=text, callback_data='None'))

    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='casino_user_menu'))
    await try_send_message(callback, 'Топ 10 коллекционеров', kb.as_markup())



