from aiogram import Router, F, MagicFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, WebAppInfo, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from handlers.buttons import (
    QUIZ_1_BTN,
    QUIZ_2_BTN,
    QUIZ_2_BTN_START,
    BACK_BUTTON,
    QUIZ_2_BTN_1
)
from handlers.texts import (
    QUIZ_MENU_MESSAGE,
    QUIZ_2_MESSAGE,
    GAME_CARD_QUIZ
)
from config import (
    QUIZ_ANSWERS,
    QUIZ_QUESTIONS,
    RESTRICT,
    RANDOM_SELECTION,
    CHARS,
    CHARS_URL
)
from .utils import try_send_message, page_menu, PageCallback, favorite_button
from database.jsondb import games
from random import shuffle


router = Router()


class QuizCallback(CallbackData, prefix="quiz1"):
    answer_id: int


class QuizState(StatesGroup):
    question = State()
    answers = State()
    games_list = State()


@router.callback_query(F.data == "quiz_menu")
async def quiz_select_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=QUIZ_1_BTN, callback_data=QuizCallback(answer_id=-1).pack()), width=1)
    kb.row(InlineKeyboardButton(text=QUIZ_2_BTN, callback_data='quiz_2'))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))
    await try_send_message(callback.message, QUIZ_MENU_MESSAGE, kb.as_markup(), './img/quiz_menu.jpeg')



@router.callback_query(QuizCallback.filter())
async def start_quiz_1(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):

    if callback_data.answer_id == -1:
        await state.set_state(QuizState.question)
        await state.update_data(
            question=0,
            answers=[]
        )

    data = await state.get_data()
    quiz_stage = data['question']
    answers = data['answers']

    # ПО окончанию викториын
    if quiz_stage == len(QUIZ_QUESTIONS):
        games = await find_game(answers)
        await state.update_data(games_list=games)
        await finish_quiz(callback, state, PageCallback(page=0, menu='finish_quiz'))
        return

    # Ответы и вопросы для вывода кнопок
    answers_for_question = QUIZ_ANSWERS[quiz_stage].keys()
    question_text = QUIZ_QUESTIONS[quiz_stage]

    # Запись тегов для финального поиска
    if callback_data.answer_id != -1:
        tags = [x for x in QUIZ_ANSWERS[quiz_stage].values()]
        if tags[callback_data.answer_id]:
            answers.append(tags[callback_data.answer_id])

    await state.update_data(
        question= quiz_stage +1,
        answers=answers
    )


    kb = InlineKeyboardBuilder()
    for i, answer in enumerate(answers_for_question):
        kb.add(InlineKeyboardButton(text=answer, callback_data=QuizCallback(answer_id=i).pack()))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='start'))
    await try_send_message(callback.message, question_text, kb.as_markup(), f'./img/quiz_1/{quiz_stage+1}vps.png')


@router.callback_query(PageCallback.filter(F.menu == 'finish_quiz'))
async def finish_quiz(callback: CallbackQuery, state: FSMContext, callback_data: PageCallback):
    page_number = callback_data.page
    data = await state.get_data()
    games_list = data['games_list']


    if page_number < 0:
        page_number = 0

    if page_number > len(games_list):
        page_number = len(games_list)-1

    kb = await page_menu(page_number, len(games_list), 'finish_quiz')
    kb.row(await favorite_button(callback.from_user.id, games[games_list[page_number]]['id']))
    kb.row(InlineKeyboardButton(text='Скачать', url=games[games_list[page_number]]['url']))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='quiz_menu'))



    photo = './img/' + games[games_list[page_number]]['picture']
    await try_send_message(callback, GAME_CARD_QUIZ.format(
        name=games_list[page_number],
        description=games[games_list[page_number]]['description']
    ),
                           reply_markup=kb.as_markup(),
                           media_path=photo
                           )


async def find_game(tags):
    dict = {}
    for t in tags:
        if t == "None":
            pass
        for i in games:
            for k in games[i]['tags']:
                if t.capitalize() == k.capitalize() and t.capitalize() not in RESTRICT:
                    try:
                        dict[i] += 1
                    except KeyError:
                        dict[i] = 1

    dict = sorted(dict.items(), key=lambda item: item[1], reverse=True)
    game_list = []
    for name, star in dict:
        if len(game_list) >= RANDOM_SELECTION:
            break
        game_list.append(name)
    shuffle(game_list)
    return game_list


@router.callback_query(F.data == 'quiz_2')
async def start_test_2(callback: CallbackQuery):
    webApp = WebAppInfo(url="https://ghoraed.github.io/hgtest/")
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=QUIZ_2_BTN_START, web_app=webApp))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='quiz_menu'))
    await try_send_message(callback, QUIZ_2_MESSAGE, reply_markup=kb.as_markup())

@router.message(MagicFilter.len(F.text) == 10)
async def pick_char(message):
    result = int(message.text)
    result = str(result)
    result = [int(x) for x in result]
    hits = {}
    for char in CHARS:
        hits[char] = 0
        for i in range(10):
            if result[i] == CHARS[char][i + 1]:
                hits[char] += 1
    hits = dict(sorted(hits.items(), key=lambda item: item[1], reverse=True))
    char_name = list(hits.keys())[0]
    char_desc = CHARS[char_name][0]
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    photo_path = BASE_DIR / "img" / "quiz_2" / f"{char_name}.png"

    photo = FSInputFile(photo_path)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=QUIZ_2_BTN_1, url=CHARS_URL[char_name]))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='quiz_menu'))
    await message.answer_photo(photo=photo, caption=f"""\nВаш персонаж: {char_name}\n{char_desc}""",
                               reply_markup=kb.as_markup())
