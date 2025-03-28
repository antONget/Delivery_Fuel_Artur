from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter, or_f

import keyboards.admin.keyboards_edit_nickname as kb
import database.requests as rq
from database.models import User
from filter.admin_filter import IsSuperAdmin
from filter.user_filter import IsRoleAdmin
from utils.error_handling import error_handler
from config_data.config import Config, load_config

from uuid import uuid4
import asyncio
import logging


router = Router()
config: Config = load_config()


class Personal(StatesGroup):
    nickname = State()


# Персонал

@router.callback_query(F.data == 'personal_nickname')
@error_handler
async def process_personal_nickname(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор пользователя для изменения никнейма
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_personal_nickname: {callback.from_user.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    list_users: list[User] = await rq.get_users_role(role=edit_role)
    if not list_users:
        await callback.answer(text=f'Нет водителей для смены никнейма', show_alert=True)
        return
    keyboard = kb.keyboards_edit_nickname(list_users=list_users,
                                          back=0,
                                          forward=2,
                                          count=6)
    await callback.message.edit_text(text=f'Выберите водителя, которому нужно изменить никнейм',
                                     reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('personal_nickname_forward'))
@error_handler
async def process_forward_nickname(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_nickname: {callback.from_user.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    list_users: list[User] = await rq.get_users_role(role=edit_role)
    forward = int(callback.data.split('_')[-1]) + 1
    back = forward - 2
    keyboard = kb.keyboards_edit_nickname(list_users=list_users,
                                          back=back,
                                          forward=forward,
                                          count=6)
    try:
        await callback.message.edit_text(text=f'Выберите водителя, которому нужно изменить никнейм',
                                         reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.edit_text(text=f'Выберитe водителя, которому нужно изменить никнейм',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('personal_nickname_back_'))
@error_handler
async def process_back_nickname(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей назад
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_back_nickname: {callback.from_user.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    list_users = await rq.get_users_role(role=edit_role)
    back = int(callback.data.split('_')[3]) - 1
    forward = back + 2
    keyboard = kb.keyboards_edit_nickname(list_users=list_users,
                                          back=back,
                                          forward=forward,
                                          count=6)
    try:
        await callback.message.edit_text(text=f'Выберите водителя, которому нужно изменить никнейм',
                                         reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.edit_text(text=f'Выберитe водителя, которому нужно изменить никнейм',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('personal_nickname'))
@error_handler
async def process_change_nickname(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Запрос нового никнейма
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_delete_user: {callback.from_user.id}')
    telegram_id = int(callback.data.split('_')[-1])
    user_info = await rq.get_user_by_id(tg_id=telegram_id)
    await state.update_data(nickname_tg_id=telegram_id)
    await callback.message.edit_text(text=f'Пришлите новый никнейм для водителя {user_info.username}/{user_info.tg_id}',
                                     reply_markup=kb.keyboard_cancel_nickname())
    await state.set_state(Personal.nickname)


@router.callback_query(F.data == 'not_change_nickname')
@error_handler
async def process_not_change_nickname(callback: CallbackQuery, bot: Bot) -> None:
    """
    Отмена изменения роли пользователя
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_not_change_nickname: {callback.from_user.id}')
    await callback.message.edit_text(text=f'Изменене никнейма отменено')


@router.message(F.text, StateFilter(Personal.nickname))
async def get_change_nickname(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем никнейм для обновления
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_change_nickname')
    nickname = message.text
    data = await state.get_data()
    tg_id = data['nickname_tg_id']
    await rq.set_user_nickname(tg_id=tg_id,
                               nickname=nickname)
    await message.answer(text='Никнейм успешно обновлен')
    await state.set_state(state=None)