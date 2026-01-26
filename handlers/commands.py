from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup

from database.users import user_show_favorites_games, get_most_favorite_games
from .utils import page_menu, favorite_button, PageCallback, try_send_message
from database.jsondb import translations, games
from .buttons import BACK_BUTTON, MY_TRANSLATES_DOWNLOAD_BTN, DOWNLOAD_BTN, POLEZNOSTI_DOWNLOAD_BTN, POLEZNOSTI_GUIDE_BTN
from .texts import GAME_CARD_TRANSLATES, POLEZNOSTI_CARD, FAVORITE_TOP_GAMES
from config import POLEZNOSTI



router = Router()


@router.callback_query(PageCallback.filter(F.menu == 'my_translates'))
async def my_translates(callback: CallbackQuery, callback_data: PageCallback):
    games_list = list(translations.values())

    page_number = max(0, min(callback_data.page, len(games_list) - 1))

    kb = await page_menu(page_number, len(games_list), 'my_translates')
    kb.row(InlineKeyboardButton(text=MY_TRANSLATES_DOWNLOAD_BTN, url=games_list[page_number]['url']))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))
    await try_send_message(callback,
        GAME_CARD_TRANSLATES.format(
        name=games_list[page_number]['name'],
        description=games_list[page_number]['description']
    ),
       reply_markup=kb.as_markup(),
       media_path='./img/' + games_list[page_number]['picture']
    )


class MyFavoritesState(StatesGroup):
    games_list = State()

@router.callback_query(F.data == 'my_favorites')
async def my_favorites(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MyFavoritesState.games_list)
    games_list = await user_show_favorites_games(callback.from_user.id)
    if not games_list:
        await callback.answer("У вас нет игр в Избранном", show_alert=True)
        return
    await state.update_data(games_list=games_list)
    await my_favorites_pagecallback(callback, PageCallback(page=0, menu='my_favorites_pagecallback'), state)

@router.callback_query(PageCallback.filter(F.menu == 'my_favorites_pagecallback'))
async def my_favorites_pagecallback(callback: CallbackQuery, callback_data: PageCallback, state: FSMContext):
    data = await state.get_data()
    games_id = data['games_list']
    games_list = list()
    for game in games:
        if games[game]['id'] in games_id:
            games_list.append(games[game])

    page_number = max(0, min(callback_data.page, len(games_list) - 1))

    kb = await page_menu(page_number, len(games_list), 'my_favorites_pagecallback')
    kb.row(await favorite_button(callback.from_user.id, games_list[page_number]['id']))
    kb.row(InlineKeyboardButton(text=DOWNLOAD_BTN, url=games_list[page_number]['url']))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))
    await try_send_message(callback, GAME_CARD_TRANSLATES.format(
        name=games_list[page_number]['name'],
        description=games_list[page_number]['description']
    ),
                           reply_markup=kb.as_markup(),
                           media_path='./img/' + games_list[page_number]['picture']
                           )


@router.callback_query(PageCallback.filter(F.menu == 'poleznosti'))
async def show_poleznosti(callback: CallbackQuery, callback_data: PageCallback):
    page_number = max(0, min(callback_data.page, len(POLEZNOSTI) - 1))

    app = POLEZNOSTI[page_number]
    kb = await page_menu(page_number, len(POLEZNOSTI), 'poleznosti')
    kb.row(InlineKeyboardButton(text=POLEZNOSTI_DOWNLOAD_BTN, url=app['download']))
    if app.get("guide"):
        kb.add(InlineKeyboardButton(text=POLEZNOSTI_GUIDE_BTN, url=app['guide']))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))

    text = POLEZNOSTI_CARD.format(name=app['title'], description=app['desc'])
    await try_send_message(callback, text, kb.as_markup(), './img/poleznosti.jpeg')

@router.callback_query(F.data == 'most_favorite_games')
async def show_most_favorite_games(callback: CallbackQuery):
    games_id_list = await get_most_favorite_games()
    games_list = list()
    for game in games:
        json_game = games[game]
        if json_game['id'] in games_id_list:
            json_game['count'] = games_id_list[json_game['id']]
            games_list.append(json_game)

    await show_most_favorite_games(callback, games_list)


async def show_most_favorite_games(callback: CallbackQuery, games_list):
    kb = InlineKeyboardBuilder()
    games_list = sorted(
        games_list,
        key=lambda game: game['count'],
        reverse=True
    )

    for i, g in enumerate(games_list):
        text = f'{i+1}. {g["name"]} - ⭐{g['count']}'
        kb.row(InlineKeyboardButton(text=text, url=g['url']))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))

    await try_send_message(callback, FAVORITE_TOP_GAMES, kb.as_markup())
