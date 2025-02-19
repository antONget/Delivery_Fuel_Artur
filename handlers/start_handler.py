from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from keyboards import start_keyboard as kb
from config_data.config import Config, load_config
from database import requests as rq
from database.models import User
from utils.error_handling import error_handler
from filter.admin_filter import check_super_admin

import logging
from datetime import datetime

router = Router()
config: Config = load_config()


class PersonalData(StatesGroup):
    fullname = State()
    personal_account = State()
    phone = State()


@router.message(CommandStart())
@router.message(F.text == 'Главное меню')
@error_handler
async def process_start_command_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработки запуска бота или ввода команды /start
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await state.set_state(state=None)

    # добавление пользователя в БД если еще его там нет
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if not user:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = "user_name"
        if await check_super_admin(telegram_id=message.from_user.id):
            role = rq.UserRole.admin
        else:
            role = rq.UserRole.user
        data_user = {"tg_id": message.from_user.id,
                     "username": username,
                     "role": role}
        await rq.add_user(data=data_user)
    else:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = "user_name"
        data_user = {"tg_id": message.from_user.id,
                     "username": username}
        await rq.add_user(data=data_user)
    # вывод клавиатуры в зависимости от роли пользователя
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    # пользователь
    if user.role == rq.UserRole.user:
        await message.answer(text='Бот доступен только авторизованным пользователям')

    # исполнитель
    elif user.role == rq.UserRole.executor:
        await message.answer(text=f'Добро пожаловать! Вы являетесь ВОДИТЕЛЕМ в проекте',
                             reply_markup=kb.keyboard_start(role=rq.UserRole.executor))

    # администратор
    elif user.role == rq.UserRole.admin:
        await message.answer(text=f'Добро пожаловать! Вы являетесь АДМИНИСТРАТОРОМ проекта',
                             reply_markup=kb.keyboard_start(role=rq.UserRole.admin))

    # партнер
    elif user.role == rq.UserRole.partner:
        await message.answer(text=f'Добро пожаловать! Вы являетесь ПАРТНЕРОМ проекта',
                             reply_markup=kb.keyboard_start(role=rq.UserRole.partner))

    if await check_super_admin(telegram_id=message.from_user.id):
        await message.answer(text=f'Изменить свою роль?',
                             reply_markup=kb.keyboard_change_role_admin())


@router.callback_query(F.data == 'change_role_admin')
@error_handler
async def change_role_admin(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Смена роли администратором
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_role_admin')
    await callback.message.edit_text(text=f'Какую роль установить?',
                                     reply_markup=kb.keyboard_select_role_admin())


@router.callback_query(F.data.startswith('select_role_'))
@error_handler
async def change_role_admin_select_role(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Смена роли администратором на выбранную
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_role_admin_select_role')
    select_role = callback.data.split('_')[-1]
    await rq.set_user_role(tg_id=callback.from_user.id, role=select_role)
    await callback.message.edit_text(text=f'Роль {select_role.upper()} успешно установлена',
                                     reply_markup=None)
    await process_start_command_user(message=callback.message, state=state, bot=bot)
