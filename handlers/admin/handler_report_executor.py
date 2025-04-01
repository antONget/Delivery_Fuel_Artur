from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter, or_f

import keyboards.admin.keyboards_report_executor as kb
import database.requests as rq
from database.models import User, Order
from filter.admin_filter import IsSuperAdmin
from filter.user_filter import IsRoleAdmin
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from utils.utils_keyboard import utils_handler_pagination_to_composite_text

from uuid import uuid4
import asyncio
import logging


router = Router()
config: Config = load_config()


class Personal(StatesGroup):
    nickname = State()


# Персонал

@router.callback_query(F.data == 'report_executor')
@error_handler
async def report_executor(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор водителя для просмотра отчета
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'report_executor: {callback.from_user.id}')
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    if not list_users:
        await callback.answer(text=f'Нет водителей', show_alert=True)
        return
    keyboard = kb.keyboards_show_report(list_users=list_users,
                                        back=0,
                                        forward=2,
                                        count=6)
    await callback.message.edit_text(text=f'Выберите водителя для просмотра отчета',
                                     reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('personal_report_forward'))
@error_handler
async def process_forward_report(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_report: {callback.from_user.id}')
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    forward = int(callback.data.split('_')[-1]) + 1
    back = forward - 2
    keyboard = kb.keyboards_show_report(list_users=list_users,
                                        back=back,
                                        forward=forward,
                                        count=6)
    try:
        await callback.message.edit_text(text=f'Выберите водителя, для просмотра отчета',
                                         reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.edit_text(text=f'Выберитe водителя, для просмотра отчета',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('personal_report_back_'))
@error_handler
async def process_back_report(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей назад
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_back_report: {callback.from_user.id}')
    data = await state.get_data()
    edit_role = data["edit_role"]
    list_users = await rq.get_users_role(role=edit_role)
    back = int(callback.data.split('_')[3]) - 1
    forward = back + 2
    keyboard = kb.keyboards_show_report(list_users=list_users,
                                        back=back,
                                        forward=forward,
                                        count=6)
    try:
        await callback.message.edit_text(text=f'Выберите водителя, для просмотра отчета',
                                         reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.message.edit_text(text=f'Выберитe водителя, для просмотра отчета',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('personal_report'))
@error_handler
async def process_personal_report(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение получения отчета
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_personal_report: {callback.from_user.id}')
    telegram_id = int(callback.data.split('_')[-1])
    await state.update_data(report_tg_id=telegram_id)

    list_orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=telegram_id,
                                                                status=rq.OrderStatus.work)
    if list_orders:
        page = 0
        text_message = f'Заказ: <i>№{list_orders[page].id}</i>\n' \
                       f'Плательщик: <i>{list_orders[page].payer}</i>\n' \
                       f'ИНН: <i>{list_orders[page].inn}</i>\n' \
                       f'Адрес: <i>{list_orders[page].address}</i>\n' \
                       f'Контактное лицо: <i>{list_orders[page].contact}</i>\n' \
                       f'Дата доставки: <i>{list_orders[page].date}</i>\n' \
                       f'Время доставки: <i>{list_orders[page].time}</i>\n' \
                       f'Количество топлива: <i>{list_orders[page].volume} литров</i>\n'
        await utils_handler_pagination_to_composite_text(list_items=list_orders,
                                                         text_message=text_message,
                                                         page=page,
                                                         text_button_select='Сменить водителя',
                                                         callback_prefix_select='selectexecutorshow',
                                                         callback_prefix_back='executorshow_back',
                                                         callback_prefix_next='executorshow_next',
                                                         callback=callback,
                                                         message=None)
    else:
        await callback.message.edit_text(text=f'Нет заказов в работе')


@router.callback_query(F.data.startswith('executorshow_back'))
@router.callback_query(F.data.startswith('executorshow_next'))
@error_handler
async def process_ordershowlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку заказов
    :param callback: {callback_prefix_back}_{page}, {callback_prefix_next}_{page}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_ordershowlist_pagination: {callback.from_user.id}')
    page: int = int(callback.data.split('_')[-1])
    action: str = callback.data.split('_')[-2]
    data = await state.get_data()
    report_tg_id = data['report_tg_id']
    list_orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=report_tg_id,
                                                                status=rq.OrderStatus.work)
    max_page = len(list_orders)
    if action == 'next':
        page += 1
    else:
        page -= 1
    if page < 0:
        page = max_page - 1
    elif page == max_page:
        page = 0
    if list_orders:
        text_message = f'Заказ: <i>№{list_orders[page].id}</i>\n' \
                       f'Плательщик: <i>{list_orders[page].payer}</i>\n' \
                       f'ИНН: <i>{list_orders[page].inn}</i>\n' \
                       f'Адрес: <i>{list_orders[page].address}</i>\n' \
                       f'Контактное лицо: <i>{list_orders[page].contact}</i>\n' \
                       f'Дата доставки: <i>{list_orders[page].date}</i>\n' \
                       f'Время доставки: <i>{list_orders[page].time}</i>\n' \
                       f'Количество топлива: <i>{list_orders[page].volume} литров</i>\n'
        await utils_handler_pagination_to_composite_text(list_items=list_orders,
                                                         text_message=text_message,
                                                         page=page,
                                                         text_button_select='Сменить водителя',
                                                         callback_prefix_select='selectexecutorshow',
                                                         callback_prefix_back='executorshow_back',
                                                         callback_prefix_next='executorshow_next',
                                                         callback=callback,
                                                         message=None)


@router.callback_query(F.data.startswith('selectexecutorshow'))
async def selectexecutorshow(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """

    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('selectexecutorshow')
    order_id = int(callback.data.split('_')[-1])
    await rq.set_order_status(order_id=order_id,
                              status=rq.OrderStatus.cancel)
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    if not list_users:
        await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
        return
    order_info: Order = await rq.get_order_id(order_id=order_id)
    keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                              back=0,
                                              forward=2,
                                              count=6,
                                              order_id=order_id)
    await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}\n\n'
                                          f'Плательщик: <i>{order_info.payer}</i>\n'
                                          f'ИНН: <i>{order_info.inn}</i>\n'
                                          f'Адрес: <i>{order_info.address}</i>\n'
                                          f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                          f'Дата доставки: <i>{order_info.date}</i>\n'
                                          f'Время доставки: <i>{order_info.time}</i>\n'
                                          f'Количество топлива: <i>{order_info.volume} литров</i>\n',
                                     reply_markup=keyboard)
