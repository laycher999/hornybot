from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.buttons import BACK_BUTTON
from handlers.utils import try_send_message, page_menu, split_list, PageCallback
from filters.admin import IsAdmin

from database.gifts import add_gift, remove_gift, get_gifts, remove_gift_by_id


router = Router()

@router.callback_query(IsAdmin(), F.data == 'admin_gifts_menu')
async def gifts_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='➕ Добавить приз', callback_data='gifts_add'),
           InlineKeyboardButton(text='📦 Просмотр призов', callback_data='gifts_check')
           )
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    kb.adjust(1,1,1)
    await try_send_message(callback, 'Выберите дальнейшее действие:', kb.as_markup())



class CheckGiftsState(StatesGroup):
    items_list = State()
    type = State()

class RemoveGift(CallbackData, prefix='remove_gift'):
    id: int
    delete: bool = False


@router.callback_query(IsAdmin(),F.data == 'gifts_check')
async def gifts_check_choose_type(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='VPN', callback_data='check:vpn'), InlineKeyboardButton(text='Boosty', callback_data='check:boosty'))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    await try_send_message(callback, 'Выбери какой тип промокода хочешь посмотреть: ', kb.as_markup())


@router.callback_query(IsAdmin(),F.data.startswith('check:'))
async def gifts_check_save_state(callback: CallbackQuery, state: FSMContext):
    type = callback.data.split(':')[-1]
    items_list = await get_gifts(type)
    if len(items_list) == 0:
        await callback.message.answer('У вас нет промокодов ' + type)
        return

    await state.update_data(
        items_list=items_list,
        type=type
    )
    await gifts_check_pagemenu(callback, PageCallback(page=0, menu='gifts_check_pagemenu'), state)

@router.callback_query(IsAdmin(),PageCallback.filter(F.menu == 'gifts_check_pagemenu'))
async def gifts_check_pagemenu(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = await state.get_data()
    items_list = data['items_list']
    type = data['type']
    number_of_items = len(items_list)
    items_list = await split_list(items_list, 12)
    page_number = max(0, min(callback_data.page, len(items_list) - 1))
    kb = await page_menu(page_number, len(items_list), 'gifts_check_pagemenu')

    for i, item in enumerate(items_list[page_number]):
        id = item['id']
        url = item['url']
        if type == 'vpn':
            url = url.split('_')[-1]
        else:
            url = url.split('/')[-2]
        kb.row(InlineKeyboardButton(text=f'❌ {url}', callback_data=RemoveGift(id=id).pack()))

    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))

    await try_send_message(callback, 'Выберите промокод для удаления', kb.as_markup())

@router.callback_query(IsAdmin(),RemoveGift.filter(F.delete == False))
async def confirm_deleting_gift(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    kb = InlineKeyboardBuilder()
    id = callback_data.id
    kb.add(InlineKeyboardButton(text='✅ Да', callback_data=RemoveGift(id=id, delete=True).pack()))
    kb.add(InlineKeyboardButton(text='❌ Нет', callback_data='admin_menu'))
    await try_send_message(callback, '⚠️ Вы точно хотите удалить промокод?', kb.as_markup())

@router.callback_query(IsAdmin(),RemoveGift.filter(F.delete == True))
async def deleting_gift(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    id = callback_data.id
    await remove_gift_by_id(id)
    kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    await try_send_message(callback, '✅ Промокод успешно удален', kb.as_markup())


class AddGiftState(StatesGroup):
    type = State()
    url = State()


@router.callback_query(IsAdmin(),F.data == 'gifts_add')
async def choose_gift_type(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='VPN', callback_data='gift:add:vpn'), InlineKeyboardButton(text='Boosty', callback_data='gift:add:boosty'))
    kb.row(InlineKeyboardButton(text=BACK_BUTTON, callback_data='admin_menu'))
    await state.set_state(AddGiftState.type)
    await try_send_message(callback, 'Выбери какой тип промокода хочешь добавить:', kb.as_markup())

@router.callback_query(IsAdmin(),F.data.startswith('gift:add:'))
async def gift_add_url(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text='Отмена', callback_data='admin_menu'))
    await state.update_data(type=callback.data.split(':')[-1])
    await state.set_state(AddGiftState.url)
    await try_send_message(callback, 'Отправь URL промокода (обычным сообщением):', kb.as_markup())

@router.message(IsAdmin(),AddGiftState.url)
async def gift_save_url(message: Message, state: FSMContext):
    kb = InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='❌ Отмена', callback_data='gift:cancel'),
        InlineKeyboardButton(text='➕ Добавить приз', callback_data='admin_menu'))
    kb.adjust(1,1)

    url = message.text.strip()
    await state.update_data(url=url)

    # необязательно, но полезно
    if not url.startswith(('http://', 'https://')):
        await message.answer('❌ Это не похоже на ссылку. Отправь корректный URL.')
        return

    data = await state.get_data()
    gift_type = data['type']

    await add_gift(type=gift_type, url=url)

    await try_send_message(message,
        f'✅ Промокод добавлен\nТип: {gift_type}\nURL: {url}', kb.as_markup()
    )


@router.callback_query(IsAdmin(),F.data.startswith('gift:cancel'))
async def gift_add_url(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder().row(InlineKeyboardButton(text='Вернуться в меню', callback_data='admin_menu'))
    data = await state.get_data()
    url = data['url']
    await remove_gift(url=url)
    await try_send_message(callback, 'Добавление приза было отменено.', kb.as_markup())
