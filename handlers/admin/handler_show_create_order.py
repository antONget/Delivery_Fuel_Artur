from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import aiogram_calendar
from aiogram.filters.callback_data import CallbackData

from keyboards.admin.keyboard_show_create_order import keyboards_executor_personal
from keyboards.partner.keyboard_order import keyboards_executor_personal
import database.requests as rq
from database.models import User, Order
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.user_filter import IsRoleAdmin
from filter.filter import validate_inn, validate_russian_phone_number
from utils.utils_keyboard import utils_handler_pagination_to_composite_text
from filter.user_filter import check_role

import logging
from datetime import datetime

config: Config = load_config()
router = Router()


@router.message(F.text == 'Необработанные заявки', IsRoleAdmin())
async def create_order_show(message: Message, state: FSMContext, bot: Bot):
    """
    просмотр созданных заказов
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('create_order_show')
    tg_id = message.from_user.id
    if await check_role(tg_id=message.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_orders_tg_id_creator_status_(tg_id_creator=tg_id,
                                                                         status=rq.OrderStatus.create)
    if list_orders:
        page = 0
        text_message = f'Выберите заказ\n\n' \
                       f'Заказ: <i>№{list_orders[page].id}</i>\n' \
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
                                                         text_button_select='Выбрать',
                                                         callback_prefix_select='selectshow',
                                                         callback_prefix_back='show_back',
                                                         callback_prefix_next='show_next',
                                                         callback=None,
                                                         message=message)
    else:
        await message.answer(text=f'Нет заказов')


@router.callback_query(F.data.startswith('show_back'))
@router.callback_query(F.data.startswith('show_next'))
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
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_orders_tg_id_creator_status_(tg_id_creator=tg_id,
                                                                         status=rq.OrderStatus.create)
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
        text_message = f'Выберите заказ\n\n' \
                       f'Заказ: <i>№{list_orders[page].id}</i>\n' \
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
                                                         text_button_select='Выбрать',
                                                         callback_prefix_select='selectshow',
                                                         callback_prefix_back='show_back',
                                                         callback_prefix_next='show_next',
                                                         callback=callback,
                                                         message=None)


@router.callback_query(F.data.startswith('selectshow'))
@error_handler
async def process_ordershowlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор заказа
    :param callback: {callback_prefix_select}_{item_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_ordershowlist_select: {callback.from_user.id}')
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    if not list_users:
        await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
        return
    order_id: int = int(callback.data.split('_')[-1])
    info_order: Order = await rq.get_order_id(order_id=order_id)
    await state.update_data(order_id=order_id)
    keyboard = keyboards_executor_personal(list_users=list_users,
                                           back=0,
                                           forward=2,
                                           count=6,
                                           order_id=order_id)

    await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}\n\n'
                                          f'Плательщик: <i>{info_order.payer}</i>\n'
                                          f'ИНН: <i>{info_order.inn}</i>\n'
                                          f'Адрес: <i>{info_order.address}</i>\n'
                                          f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                          f'Дата доставки: <i>{info_order.date}</i>\n'
                                          f'Время доставки: <i>{info_order.time}</i>\n'
                                          f'Количество топлива: <i>{info_order.volume} литров</i>\n',
                                     reply_markup=keyboard)
