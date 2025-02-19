from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from keyboards.start_keyboard import keyboard_start
from keyboards.user.keyboard_personal_data import keyboards_get_contact
import database.requests as rq
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.filter import validate_russian_phone_number

import logging
from datetime import datetime

config: Config = load_config()
router = Router()


class PersonalData(StatesGroup):
    fullname = State()
    personal_account = State()
    phone = State()


@router.message(F.text, StateFilter(PersonalData.fullname))
@error_handler
async def get_full_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем полное имя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_full_name: {message.chat.id}')
    full_name = message.text
    await rq.set_user_fullname(tg_id=message.from_user.id,
                               fullname=full_name)
    await message.answer(text=f'Пришлите номер вашего лицевого счета')
    await state.set_state(state=PersonalData.personal_account)


@router.message(F.text, StateFilter(PersonalData.personal_account))
@error_handler
async def get_personal_account(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем лицевой счет
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_personal_account: {message.chat.id}')
    personal_account = message.text
    await rq.set_user_personal_account(tg_id=message.from_user.id,
                                       personal_account=personal_account)
    await message.answer(text=f'Укажите ваш номер телефона, можете воспользоваться кнопкой'
                              f' "Поделиться ☎️" расположенной ниже 👇',
                         reply_markup=keyboards_get_contact())
    await state.set_state(state=PersonalData.phone)


@router.message(StateFilter(PersonalData.phone))
async def get_phone_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем номер телефона проверяем его на валидность и заносим его в БД
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    # если номер телефона отправлен через кнопку "Поделится"
    if message.contact:
        phone = str(message.contact.phone_number)
    # если введен в поле ввода
    else:
        phone = message.text
        # проверка валидности отправленного номера телефона, если не валиден просим ввести его повторно
        if not validate_russian_phone_number(phone):
            await bot.edit_message_text(text="Неверный формат номера, повторите ввод.")
            return
    await rq.set_user_phone(tg_id=message.from_user.id,
                            phone=phone)
    await state.set_state(state=None)
    await message.answer(text='Выберите раздел',
                         reply_markup=keyboard_start(role=rq.UserRole.user))
