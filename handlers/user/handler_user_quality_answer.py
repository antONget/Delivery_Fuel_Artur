from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboard_user_quality_answer as kb
import database.requests as rq
from database.models import User, Order
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_text

from config_data.config import Config, load_config

import logging
from datetime import datetime
import random
import asyncio

config: Config = load_config()
router = Router()


class StageQuality(StatesGroup):
    state_comment = State()


@router.callback_query(F.data.startswith('make_quality_'))
@error_handler
async def quality_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Качество выполнения заявки
    :param callback: make_quality_{order_id}
    :param bot:
    :param state:
    :return:
    """
    logging.info('quality_order')
    order_id: int = int(callback.data.split('_')[-1])
    await state.update_data(order_id=order_id)
    await callback.message.edit_text(text='Пожалуйста оцените качество решения вашего вопроса!',
                                     reply_markup=kb.keyboard_quality_answer(order_id=order_id))


@router.callback_query(F.data.startswith('quality_'))
@error_handler
async def quality_answer_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Качество решения заявки
    :param callback: quality_5_{order_id}
    :param bot:
    :param state:
    :return:
    """
    logging.info('quality_answer_order')
    order_id = int(callback.data.split('_')[-1])
    quality = int(callback.data.split('_')[1])
    await rq.set_order_quality(order_id=order_id, quality=quality)
    info_order: Order = await rq.get_order_id(order_id=order_id)
    info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    if quality == 5:
        await callback.message.edit_text(text='Благодарим за обратную связь, нам очень важна ваша оценка!',
                                         reply_markup=None)
        text_quality = '⭐' * quality
        await bot.send_message(chat_id=info_order.executor,
                               text=f"Пользователь <a href='tg://user?id={callback.from_user.id}'>"
                                    f"{callback.from_user.username}</a> оценил качество выполнения заявки"
                                    f" № {info_order.id} на {text_quality}")
    elif quality > 0:
        await callback.message.edit_text(text='Благодарим за обратную связь, нам очень важна ваша оценка!\n'
                                              'Укажите почему вы снизили оценку?',
                                         reply_markup=kb.keyboard_pass_comment())
        await state.update_data(quality=quality)
        await state.set_state(StageQuality.state_comment)
    else:
        await callback.message.edit_text(text='Благодарим за обратную связь, постараемся решить вашу проблему!',
                                         reply_markup=None)
        await bot.send_message(chat_id=info_order.executor,
                               text=f"Пользователь <a href='tg://user?id={info_order.tg_id}'>{info_user.username}</a> "
                                    f"указал, что заявка №{info_order.id} не выполнена")
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await send_message_admins_text(bot=bot,
                                       text=f"Пользователь "
                                            f"<a href='tg://user?id={info_order.tg_id}'>{info_user.username}</a>"
                                            f" указал, что заявка №{info_order.id} не выполнена исполнителем "
                                            f"<a href='tg://user?id={info_order.executor}'>"
                                            f"{executor.username}</a>",
                                       keyboard=None)
    await callback.answer()


@router.message(StateFilter(StageQuality.state_comment), F.text)
@error_handler
async def get_comment_user(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем комментарий к выполнению заявки от пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_comment_user')
    data = await state.get_data()
    order_id = data['order_id']
    quality = data['quality']
    await rq.set_order_comment(order_id=int(order_id), comment=message.text)
    text_quality = '⭐' * quality
    info_order: Order = await rq.get_order_id(order_id=int(order_id))
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    await bot.send_message(chat_id=info_order.executor,
                           text=f"Пользователь <a href='tg://user?id={info_order.tg_id}'>{info_user.username}</a> "
                                f"оценил вашу помощь на вопрос № {info_order.id} на {text_quality}.\n"
                                f"<i>Комментарий</i>: {message.text}")
    await send_message_admins_text(bot=bot,
                                   text=f"Пользователь <a href='tg://user?id={info_order.tg_id}'>{info_user.username}</a> "
                                        f"оценил вашу помощь на вопрос № {info_order.id} на {text_quality}.\n"
                                        f"<i>Комментарий</i>: {message.text}",
                                   keyboard=None)
    await message.answer(text='Ваша оценка и комментарий передана специалисту, спасибо!')
    await state.set_state(state=None)


@router.callback_query(F.data == "pass_comment")
@error_handler
async def pass_comment(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Пропускаем добавление комментария
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('pass_comment')
    data = await state.get_data()
    order_id = data['order_id']
    quality = data['quality']
    text_quality = '⭐' * quality
    info_order: Order = await rq.get_order_id(order_id=int(order_id))
    info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    await bot.send_message(chat_id=info_order.executor,
                           text=f"Пользователь <a href='tg://user?id={info_order.tg_id}'>{info_user.username}</a> "
                                f"оценил вашу помощь на вопрос № {info_order.id} на {text_quality}.\n"
                                f"<i>Комментарий</i>: отсутствует")
    await send_message_admins_text(bot=bot,
                                   text=f"Пользователь <a href='tg://user?id={info_order.tg_id}'>{info_user.username}</a> "
                                        f"оценил вашу помощь на вопрос № {info_order.id} на {text_quality}.\n"
                                        f"<i>Комментарий</i>: отсутствует",
                                   keyboard=None)
    await callback.message.edit_text(text='Ваша оценка передана специалисту, спасибо!',
                                     reply_markup=None)
    await state.set_state(state=None)
