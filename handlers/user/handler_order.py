from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

import keyboards.user.keyboard_order as kb
from keyboards.start_keyboard import keyboard_start
import database.requests as rq
from database.models import User
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_photo, send_message_admins_text
from config_data.config import Config, load_config

import logging
from datetime import datetime, timedelta

config: Config = load_config()
router = Router()


class OrderState(StatesGroup):
    text_order = State()
    photo_order = State()
    deadline = State()


@router.message(F.text == 'Подать заявку/обращение')
@error_handler
async def press_button_order(message: Message, bot: Bot) -> None:
    """
    Запуск процедуры отправки заявки
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_order: {message.chat.id}')
    await message.answer(text=f'Выберите раздел размещения заявки/обращения',
                         reply_markup=kb.keyboard_type_report())


@router.callback_query(F.data.startswith('type_order_'))
@error_handler
async def get_type_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Изменить данные пользователя
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_type_order: {callback.message.chat.id}')
    type_order = callback.data.split('_')[-1]
    await state.update_data(type_order=type_order)
    await callback.message.edit_text(text=f'Пришлите описание вашей заявки',
                                     reply_markup=None)
    await state.update_data(photo_order=[])
    await state.set_state(OrderState.text_order)
    await callback.answer()


@router.message(F.text, StateFilter(OrderState.text_order))
@router.message(F.photo, StateFilter(OrderState.photo_order))
@error_handler
async def get_text_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_text_order: {message.chat.id}')
    if message.text:
        text_order = message.text
        await state.update_data(text_order=text_order)
        await message.answer(text='Ваше сообщение получено можете добавить фото',
                             reply_markup=kb.keyboard_send_order())
    elif message.photo:
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        photo_order: list = data['photo_order']
        photo_order.append(photo_id)
        await state.update_data(photo_order=photo_order)
        await message.answer(text='Ваше сообщение получено можете добавить еще фото',
                             reply_markup=kb.keyboard_send_order())


@router.callback_query(F.data.startswith('send_order_'))
@error_handler
async def send_order(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_change_attribute: {callback.from_user.id} ')
    answer = callback.data.split('_')[-1]
    if answer == 'photo':
        await callback.message.edit_text(text='Пришлите фото к заявке',
                                         reply_markup=None)
        await state.set_state(OrderState.photo_order)
    elif answer == 'continue':
        await state.set_state(OrderState.deadline)
        await callback.message.edit_text(text='Пришлите срок выполнения заявки в днях',
                                         reply_markup=None)
    await callback.answer()


@router.message(F.text, StateFilter(OrderState.deadline))
@error_handler
async def get_deadline(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем срок выполнения заявки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_deadline: {message.from_user.id}')
    if not message.text.isdigit():
        await message.answer(text='Некорректно указано количество дней для выполнения заявки')
    else:
        deadline = int(message.text)
        data = await state.get_data()
        current_date = datetime.now()
        deadline_data = current_date + timedelta(days=deadline)
        deadline_data_str = deadline_data.strftime('%d-%m-%Y %H:%M')
        current_date_str = current_date.strftime('%d-%m-%Y %H:%M')
        data_order = {"tg_id": message.from_user.id,
                      "type_order": data["type_order"],
                      "text_order": data["text_order"],
                      "photo_ids": ','.join(data["photo_order"]) if data["photo_order"] else '',
                      "status": rq.OrderStatus.create,
                      "date_create": current_date_str,
                      "deadline": deadline_data_str}
        order_id: int = await rq.add_order(data=data_order)
        await message.answer(text=f'Ваша обращение передана, ей присвоен номер № {order_id}')
        if data["photo_order"]:
            await send_message_admins_photo(bot=bot,
                                            list_ids=data["photo_order"],
                                            caption=data["text_order"])
            await send_message_admins_text(bot=bot,
                                           text=f'Пользователь <a href="tg://user?id={message.from_user.id}">'
                                                f'{message.from_user.username}</a> разместил заявку'
                                                f' № {order_id} - {data["type_order"]}',
                                           keyboard=kb.keyboard_assign_performer(order_id=order_id))
        else:
            await send_message_admins_text(bot=bot,
                                           text=f'Пользователь <a href="tg://user?id={message.from_user.id}">'
                                                f'{message.from_user.username}</a> разместил заявку'
                                                f' № {order_id} - - {data["type_order"]}\n\n'
                                                f'{data["text_order"]}',
                                           keyboard=kb.keyboard_assign_performer(order_id=order_id))