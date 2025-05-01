from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup


from keyboards.partner.keyboard_order_change import keyboard_edit
import database.requests as rq
from database.models import Order
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.filter import validate_inn
from utils.utils_keyboard import utils_handler_pagination_to_composite_text
from filter.user_filter import check_role

import logging

config: Config = load_config()
router = Router()


class OrderReqChange(StatesGroup):
    payer_state = State()
    inn_state = State()


@router.callback_query(F.data == 'change_order')
async def change_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Редактирование заказа
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order')
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    if list_orders:
        page = 0
        text_message = f'Выберите заказ для изменения реквизитов\n\n' \
                       f'Заказ №{list_orders[page].id}\n' \
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
                                                         callback_prefix_select='selectreqchange',
                                                         callback_prefix_back='reqchange_back',
                                                         callback_prefix_next='reqchange_next',
                                                         callback=callback,
                                                         message=None)
    else:
        await callback.message.answer(text=f'Нет заказов для изменения реквизитов')


@router.callback_query(F.data.startswith('reqchange_back'))
@router.callback_query(F.data.startswith('reqchange_next'))
@error_handler
async def process_orderreqchangelist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку заказов
    :param callback: {callback_prefix_back}_{page}, {callback_prefix_next}_{page}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_orderreqchangetlist_pagination: {callback.from_user.id}')
    page: int = int(callback.data.split('_')[-1])
    action: str = callback.data.split('_')[-2]
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
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
        text_message = f'Выберите заказ для изменения реквизитов\n\n' \
                       f'Заказ №{list_orders[page].id}\n' \
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
                                                         callback_prefix_select='selectreqchange',
                                                         callback_prefix_back='reqchange_back',
                                                         callback_prefix_next='reqchange_next',
                                                         callback=callback,
                                                         message=None)


@router.callback_query(F.data.startswith('selectreqchange'))
@error_handler
async def process_orderreqchangelist_select(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор заказа для повтора
    :param callback: {callback_prefix_select}_{item_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_orderreqchangelist_select:{callback.data} {callback.from_user.id}')
    page: int = int(callback.data.split('_')[-1])
    # print(page)
    info_order: Order = await rq.get_order_id(page)
    await state.update_data(order_id=page)
    text_message = f'Заказ №{page}\n' \
                   f'Плательщик: <i>{info_order.payer}</i>\n' \
                   f'ИНН: <i>{info_order.inn}</i>\n' \
                   f'Адрес: <i>{info_order.address}</i>\n' \
                   f'Контактное лицо: <i>{info_order.contact}</i>\n' \
                   f'Дата доставки: <i>{info_order.date}</i>\n' \
                   f'Время доставки: <i>{info_order.time}</i>\n' \
                   f'Количество топлива: <i>{info_order.volume} литров</i>\n'
    await callback.message.edit_text(text=text_message,
                                     reply_markup=keyboard_edit())


@router.callback_query(F.data.startswith('reqchangeorder_'))
async def change_order_payer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('reqchange_order_payer')
    action = callback.data.split('_')[-1]
    data = await state.get_data()
    order_id = data['order_id']
    if action == 'payer':
        await callback.message.edit_text(text=f'Пришлите новое название ПЛАТЕЛЬЩИКА для заказ №{order_id}')
        await state.set_state(OrderReqChange.payer_state)
    if action == 'inn':
        await callback.message.edit_text(text=f'Пришлите новое ИНН для заказ №{order_id}')
        await state.set_state(OrderReqChange.inn_state)
    if action == 'confirm':
        await change_order(callback=callback, state=state, bot=bot)


@router.message(F.text, StateFilter(OrderReqChange.payer_state))
@router.message(F.text, StateFilter(OrderReqChange.inn_state))
@error_handler
async def process_get_input_payer(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем название плательщика и ИНН
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_input_payer: {message.from_user.id}')
    answer = message.text
    data = await state.get_data()
    order_id = data['order_id']
    if await state.get_state() == OrderReqChange.payer_state:
        await rq.set_order_payer(order_id=order_id, payer=answer)
        await state.set_state(state=None)
    if await state.get_state() == OrderReqChange.inn_state:
        if validate_inn(answer):
            await rq.set_order_inn(order_id=order_id, inn=answer)
            await state.set_state(state=None)
        else:
            await message.answer(text=f'ИНН введен некорректно, он должен содержать 10 цифр')
            return
    info_order: Order = await rq.get_order_id(order_id)
    text_message = f'Заказ №{order_id}\n' \
                   f'Плательщик: <i>{info_order.payer}</i>\n' \
                   f'ИНН: <i>{info_order.inn}</i>\n' \
                   f'Адрес: <i>{info_order.address}</i>\n' \
                   f'Контактное лицо: <i>{info_order.contact}</i>\n' \
                   f'Дата доставки: <i>{info_order.date}</i>\n' \
                   f'Время доставки: <i>{info_order.time}</i>\n' \
                   f'Количество топлива: <i>{info_order.volume} литров</i>\n'
    await message.answer(text=text_message,
                         reply_markup=keyboard_edit())
