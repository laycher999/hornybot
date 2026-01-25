from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.utils import try_send_message, PageCallback, page_menu, favorite_button, split_list
from .texts import FIND_GAME_SELECT_PLATFORM_MESSAGE, GAME_CARD_QUIZ
from .buttons import BACK_BUTTON, DOWNLOAD_BTN, FIND_BTN
from database.jsondb import android_tags, pc_tags, games
router = Router()

class FindGameState(StatesGroup):
    platform = State()
    tags = State()
    game_list = State()

@router.callback_query(F.data == "find_game")
async def select_platform(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(FindGameState.platform)
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='🖥 PC', callback_data='fg:platform:pc'))
    kb.add(InlineKeyboardButton(text='📱 Android', callback_data='fg:platform:android'))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))

    await try_send_message(callback,
                           FIND_GAME_SELECT_PLATFORM_MESSAGE,
                           kb.as_markup(),
                            './img/find_game_platform.jpeg')

@router.callback_query(F.data.startswith("fg:platform:"))
async def platform_selected(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.split(":")[-1]
    await state.update_data(platform=platform, tags = [])
    await select_tags(callback, state, PageCallback(page=0,menu='find_game_tags'))

@router.callback_query(F.data.startswith('fg:tag:'))
async def tag_selected(callback: CallbackQuery, state: FSMContext):
    tag = callback.data.split(":")[-1]
    data = await state.get_data()
    tags = data['tags']
    if tag.startswith('❌'):
        tags.pop(tag)
    else:
        tags.append(tag)
    await state.update_data(tags=tags)
    await select_tags(callback, state, PageCallback(page=0,menu='find_game_tags'))

@router.callback_query(PageCallback.filter(F.menu == 'find_game_tags'))
async def select_tags(callback: CallbackQuery, state: FSMContext, callback_data: PageCallback):
    await state.set_state(FindGameState.tags)
    data = await state.get_data()
    platform = data['platform']

    if platform == '📱 Android':
        tags = android_tags
    else:
        tags = pc_tags

    tags = await split_list(tags, 18) # разбиваю список на списки по 18 элементов

    page_number = max(0, min(callback_data.page, len(tags) - 1))
    kb = await page_menu(page_number, len(tags), 'find_game_tags')
    kb.row(InlineKeyboardButton(text=FIND_BTN, callback_data='start_find'))
    selected_tags = data.get('tags', [])

    # разбиваем на подсписки по 3
    for chunk in [tags[page_number][i:i + 2] for i in range(0, len(tags[page_number]), 2)]:
        buttons = []
        for t in chunk:
            # текст кнопки для пользователя
            text = f"{t}  {'❌' if t in selected_tags else '➕'}"
            buttons.append(InlineKeyboardButton(text=text, callback_data='fg:tag:' + t))
        # добавляем ряд из 3 кнопок
        kb.row(*buttons)
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))

    await try_send_message(
        callback,
        f"✅ Платформа: <b>{platform.upper()}</b>\n\n"
        "Выбери жанры (можно несколько):",
        kb.as_markup(),
        "./img/find_game_tags.jpeg"
    )

@router.callback_query(F.data == 'start_find')
async def sort_tagged_games(callback: CallbackQuery, state: FSMContext):
    game_list = []
    data = await state.get_data()
    tags = data['tags']

    for i in games:
        hit_count = 0
        for tag in tags:
            if tag in games[i]['tags']:
                if hit_count == len(tags)-1:
                    game_list.append(games[i])
                    pass
                hit_count += 1
    await state.update_data(game_list=game_list)
    if game_list == []:
        await callback.message.answer("Ничего не найдено")
        await platform_selected(callback, state)
        return
    else:
        await find_game_pagemenu(callback, state, PageCallback(page=0,menu='find_game_pagemenu'))

@router.callback_query(PageCallback.filter(F.menu == 'find_game_pagemenu'))
async def find_game_pagemenu(callback: CallbackQuery, state: FSMContext, callback_data: PageCallback):
    data = await state.get_data()
    game_list = data['game_list']
    page_number = max(0, min(callback_data.page, len(game_list) - 1))

    name = game_list[page_number]['name']
    game_id = game_list[page_number]['id']
    desc = game_list[page_number]['description']
    url = game_list[page_number]['url']
    photo = './img/' + game_list[page_number]['picture']

    kb = await page_menu(page_number, len(game_list), 'find_game_pagemenu')
    kb.row(await favorite_button(callback.from_user.id, game_id))
    kb.row(InlineKeyboardButton(text=DOWNLOAD_BTN, url=url))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))

    text = GAME_CARD_QUIZ.format(name=name, description=desc)
    await try_send_message(callback, text, kb.as_markup(), photo)
