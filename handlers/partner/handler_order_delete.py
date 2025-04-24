from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import aiogram_calendar
from aiogram.filters.callback_data import CallbackData

from keyboards.partner.keyboard_order_delete import keyboard_delete
from keyboards.partner.keyboard_order import keyboards_executor_personal
import database.requests as rq
from database.models import User, Order, OrderAdminEdit
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from utils.send_admins import send_message_admins_text
from utils.utils_keyboard import utils_handler_pagination_to_composite_text
from filter.user_filter import check_role

import logging
from datetime import datetime

config: Config = load_config()
router = Router()


class OrderChange(StatesGroup):
    payer_state = State()
    inn_state = State()
    address_state = State()
    contact_state = State()
    date_state = State()
    time_state = State()
    volume_state = State()


@router.callback_query(F.data == 'delete_order')
async def delete_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Запуск процесса удаления заказ
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('delete_order')
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_orders_tg_id_creator_status(tg_id_creator=tg_id,
                                                                        status=rq.OrderStatus.create)
    print(list_orders)
    if list_orders:
        page = 0
        text_message = f'Выберите заказ для удаления\n\n' \
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
                                                         callback_prefix_select='selectdelete',
                                                         callback_prefix_back='delete_back',
                                                         callback_prefix_next='delete_next',
                                                         callback=callback,
                                                         message=None)
    else:
        await callback.message.answer(text=f'Нет заказов для удаления')


@router.callback_query(F.data.startswith('delete_back'))
@router.callback_query(F.data.startswith('delete_next'))
@error_handler
async def process_orderdeletelist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку заказов
    :param callback: {callback_prefix_back}_{page}, {callback_prefix_next}_{page}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_orderdeletelist_pagination: {callback.from_user.id}')
    page: int = int(callback.data.split('_')[-1])
    action: str = callback.data.split('_')[-2]
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_orders_tg_id_creator_status(tg_id_creator=tg_id,
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
        text_message = f'Выберите заказ для удаления\n\n' \
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
                                                         callback_prefix_select='selectdelete',
                                                         callback_prefix_back='backdelete',
                                                         callback_prefix_next='nextdelete',
                                                         callback=callback,
                                                         message=None)


@router.callback_query(F.data.startswith('selectdelete'))
@error_handler
async def process_orderdeletelist_select(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор заказа для удаления
    :param callback: {callback_prefix_select}_{item_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_orderdeletelist_select: {callback.from_user.id}')
    page: int = int(callback.data.split('_')[-1])
    info_order: Order = await rq.get_order_id(page)
    await state.update_data(order_id=page)
    text_message = f'Заказ: <i>№{info_order.id}</i>\n' \
                   f'Плательщик: <i>{info_order.payer}</i>\n' \
                   f'ИНН: <i>{info_order.inn}</i>\n' \
                   f'Адрес: <i>{info_order.address}</i>\n' \
                   f'Контактное лицо: <i>{info_order.contact}</i>\n' \
                   f'Дата доставки: <i>{info_order.date}</i>\n' \
                   f'Время доставки: <i>{info_order.time}</i>\n' \
                   f'Количество топлива: <i>{info_order.volume} литров</i>\n'
    await callback.message.edit_text(text=text_message,
                                     reply_markup=keyboard_delete())


@router.callback_query(F.data.startswith('deleteorder'))
@error_handler
async def process_deleteorder(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение удаления заказа
    :param callback: repeatorder_confirm, repeatorder_edit
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_deleteorder: {callback.from_user.id}')
    action = callback.data.split('_')[-1]
    data = await state.get_data()
    order_id = data['order_id']
    info_order = await rq.get_order_id(order_id=order_id)
    if action == 'confirm':
        # получаем информацию о списке сообщений с заказом у администрвторов
        messages_order: list[OrderAdminEdit] = await rq.get_order_admin_edit(order_id=order_id)
        # пытаемся удалить заказ
        for info_message in messages_order:
            try:
                await bot.delete_message(chat_id=info_message.chat_id,
                                         message_id=info_message.message_id)
            except:
                pass
        await rq.delete_order_admin_edit(order_id=order_id)
        await send_message_admins_text(bot=bot,
                                       text=f'Заказ №{order_id} был удален <a href="tg://user?id={callback.from_user.id}">'
                                            f'{callback.from_user.username}</a>',
                                       keyboard=None)
        # удаляем заказ
        await rq.delete_order(order_id=order_id)
        try:
            await callback.message.edit_text(text=f'Удаление заказа №{order_id} прошло успешно')
        except:
            await callback.message.edit_text(text=f'Удаление заказа №{order_id} прошло успешно.')
    else:
        await callback.message.edit_text(text=f'Удаление заказа №{order_id} отменено')


