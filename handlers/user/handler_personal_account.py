from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

import keyboards.user.keyboard_personal_account as kb
from keyboards.start_keyboard import keyboard_start
import database.requests as rq
from database.models import User
from utils.error_handling import error_handler
from config_data.config import Config, load_config

import logging
from datetime import datetime, timedelta

config: Config = load_config()
router = Router()


class PersonalData(StatesGroup):
    change = State()


@router.message(F.text == 'Личный кабинет 👤')
@error_handler
async def press_button_rate(message: Message, bot: Bot) -> None:
    """
    Выбор тарифа для подписки
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_rate: {message.chat.id}')
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    await message.answer(text=f'Ваши персональные данные. При необходимости можете их изменить',
                         reply_markup=kb.keyboard_change_personal_data(info_user=info_user))


@router.callback_query(F.data.startswith('change_personal_data_'))
@error_handler
async def change_attribute_personal_data(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Изменить данные пользователя
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'change_attribute_personal_data: {callback.message.chat.id}')
    attribute = callback.data.split('_')[-1]
    if attribute == 'confirm':
        await callback.message.delete()
        await callback.message.answer(text='Выберите раздел',
                                      reply_markup=keyboard_start(role=rq.UserRole.user))
        await state.set_state(state=None)
    else:
        await callback.message.delete()
        await state.update_data(change_attribute=attribute)
        await callback.message.answer(text=f'Пришлите данные для обновления')
        await state.set_state(PersonalData.change)
    await callback.answer()


@router.message(F.text, StateFilter(PersonalData.change))
@error_handler
async def process_change_attribute(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_change_attribute: {message.chat.id}')
    data = await state.get_data()
    attribute = data['change_attribute']
    if attribute == 'fullname':
        await rq.set_user_fullname(tg_id=message.from_user.id,
                                   fullname=message.text)
    elif attribute == 'personalaccount':
        await rq.set_user_personal_account(tg_id=message.from_user.id,
                                           personal_account=message.text)
    elif attribute == 'phone':
        await rq.set_user_phone(tg_id=message.from_user.id,
                                phone=message.text)
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    await message.answer(text=f'Ваши персональные данные. При необходимости можете их изменить',
                         reply_markup=kb.keyboard_change_personal_data(info_user=info_user))
