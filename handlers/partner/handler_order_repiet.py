from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import aiogram_calendar
from aiogram.filters.callback_data import CallbackData

from keyboards.partner.keyboard_order_repiet import keyboard_repiet, keyboard_action_repiet, keyboards_payer, \
    keyboards_inn, keyboards_contact, keyboard_time_interval, keyboard_time_interval_r
from keyboards.partner.keyboard_order import keyboards_executor_personal
from keyboards.partner.keyboard_order import keyboard_delete_partner
import database.requests as rq
from database.models import User, Order
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.user_filter import IsRoleUser
from filter.filter import validate_inn, validate_russian_phone_number, validate_volume
from utils.utils_keyboard import utils_handler_pagination_to_composite_text
from filter.user_filter import check_role

import logging
from datetime import datetime, timedelta

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


class OrderRepeat(StatesGroup):
    date_state = State()
    time_state = State()
    volume_state = State()


@router.callback_query(F.data == 'repeat_order')
async def repeat_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Запуск процесса создания нового заказа
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('repeat_order')
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    print(len(list_orders))
    if list_orders:
        page = 0
        text_message = f'Выберите заказ для повторной отправки\n\n' \
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
                                                         callback_prefix_select='selectrepeat',
                                                         callback_prefix_back='repeat_back',
                                                         callback_prefix_next='repeat_next',
                                                         callback=callback,
                                                         message=None)
    else:
        await callback.message.answer(text=f'Нет заказов для их повторения')


@router.callback_query(F.data.startswith('repeat_back'))
@router.callback_query(F.data.startswith('repeat_next'))
@error_handler
async def process_orderrepeatlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку заказов
    :param callback: {callback_prefix_back}_{page}, {callback_prefix_next}_{page}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_orderrepeatlist_pagination: {callback.from_user.id}')
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
        text_message = f'Выберите заказ для повторной отправки\n\n' \
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
                                                         callback_prefix_select='selectrepeat',
                                                         callback_prefix_back='repeat_back',
                                                         callback_prefix_next='repeat_next',
                                                         callback=callback,
                                                         message=None)


@router.callback_query(F.data.startswith('selectrepeat'))
@error_handler
async def process_orderrepeatlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор заказа для повтора
    :param callback: {callback_prefix_select}_{item_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_orderrepeatlist_select: {callback.from_user.id}')
    page: int = int(callback.data.split('_')[-1])
    print(page)
    info_order: Order = await rq.get_order_id(page)
    await state.update_data(order_id=page)
    text_message = f'Выберите заказ для повторной отправки\n\n' \
                   f'Плательщик: <i>{info_order.payer}</i>\n' \
                   f'ИНН: <i>{info_order.inn}</i>\n' \
                   f'Адрес: <i>{info_order.address}</i>\n' \
                   f'Контактное лицо: <i>{info_order.contact}</i>\n' \
                   f'Дата доставки: <i>{info_order.date}</i>\n' \
                   f'Время доставки: <i>{info_order.time}</i>\n' \
                   f'Количество топлива: <i>{info_order.volume} литров</i>\n'
    await callback.message.edit_text(text=text_message,
                                     reply_markup=keyboard_repiet())


@router.callback_query(F.data.startswith('repeatorder'))
@error_handler
async def process_repeatorder(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку заказов
    :param callback: repeatorder_confirm, repeatorder_edit
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_repeatorder: {callback.from_user.id}')
    action = callback.data.split('_')[-1]
    data = await state.get_data()
    order_id = data['order_id']
    info_order = await rq.get_order_id(order_id=order_id)
    if action == 'confirm':
        calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
        calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        date1 = current_date.strftime('%d/%m/%Y')
        # преобразуем дату в список
        list_date1 = date1.split('/')
        await callback.message.edit_text(
            "Укажите желаемую дату доставки топлива",
            reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
        )
        await state.set_state(OrderRepeat.date_state)
        # order_data = {"tg_id": callback.from_user.id,
        #               "payer": data['payer_order'] if data.get('payer_order') else info_order.payer,
        #               "inn": data['inn_order'] if data.get('inn_order') else info_order.inn,
        #               "address": data['address_order'] if data.get('address_order') else info_order.address,
        #               "contact": data['contact_order'] if data.get('contact_order') else info_order.contact,
        #               "date": data['date_order'] if data.get('date_order') else info_order.date,
        #               "time": data['time_order'] if data.get('time_order') else info_order.time,
        #               "volume": data['volume_order'] if data.get('volume_order') else info_order.volume,
        #               "status": rq.OrderStatus.create,
        #               "date_create": datetime.now().strftime('%d.%m.%Y %H:%M')}
        # order_id: int = await rq.add_order(data=order_data)
        # await state.update_data(order_id=order_id)
        # list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
        # if not list_users:
        #     await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
        #     return
        # keyboard = keyboards_executor_personal(list_users=list_users,
        #                                        back=0,
        #                                        forward=2,
        #                                        count=6,
        #                                        order_id=order_id)
        # list_admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
        # admins_tg_id: list[int] = [admin.tg_id for admin in list_admins]
        # info_order: Order = await rq.get_order_id(order_id=order_id)
        # if callback.from_user.id in admins_tg_id:
        #     await callback.message.answer(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}'
        #                                        f'Плательщик: <i>{info_order.payer}</i>\n'
        #                                        f'ИНН: <i>{info_order.inn}</i>\n'
        #                                        f'Адрес: <i>{info_order.address}</i>\n'
        #                                        f'Контактное лицо: <i>{info_order.contact}</i>\n'
        #                                        f'Дата доставки: <i>{info_order.date}</i>\n'
        #                                        f'Время доставки: <i>{info_order.time}</i>\n'
        #                                        f'Количество топлива: <i>{info_order.volume} литров</i>\n',
        #                                   reply_markup=keyboard)
        # else:
        #     await callback.message.edit_text(text=f'Заказ № {order_id} создан и передан администратору. '
        #                                           f'О смене статуса заказа мы вас оповестим')
        #     admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
        #     for chat_id in admins:
        #         try:
        #             await bot.send_message(chat_id=chat_id.tg_id,
        #                                    text=f'Заказ № {order_id} создан партнером'
        #                                         f' <a href="tg://user?id={callback.from_user.id}">'
        #                                         f'{callback.from_user.username}</a>\n\n'
        #                                         f'Плательщик: <i>{info_order.payer}</i>\n'
        #                                         f'ИНН: <i>{info_order.inn}</i>\n'
        #                                         f'Адрес: <i>{info_order.address}</i>\n'
        #                                         f'Контактное лицо: <i>{info_order.contact}</i>\n'
        #                                         f'Дата доставки: <i>{info_order.date}</i>\n'
        #                                         f'Время доставки: <i>{info_order.time}</i>\n'
        #                                         f'Количество топлива: <i>{info_order.volume} литров</i>\n'
        #                                         f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
        #                                    reply_markup=keyboard)
        #         except:
        #             pass
        # await state.clear()
    else:
        await callback.message.edit_text(text=f"Плательщик: <i>"
                                              f"{data['payer_order'] if data.get('payer_order') else info_order.payer}"
                                              f"</i>\n"
                                              f"ИНН: <i>"
                                              f"{data['inn_order'] if data.get('inn_order') else info_order.inn}"
                                              f"</i>\n"
                                              f"Адрес: <i>"
                                              f"{data['address_order'] if data.get('address_order') else info_order.address}"
                                              f"</i>\n"
                                              f"Контактное лицо: <i>"
                                              f"{data['contact_order'] if data.get('contact_order') else info_order.contact}</i>\n"
                                              f"Дата доставки: <i>"
                                              f"{data['date_order'] if data.get('date_order') else info_order.date}"
                                              f"</i>\n"
                                              f"Время доставки: <i>"
                                              f"{data['time_order'] if data.get('time_order') else info_order.time}"
                                              f"</i>\n"
                                              f"Количество топлива: <i>"
                                              f"{data['volume_order'] if data.get('volume_order') else info_order.volume}"
                                              f" литров</i>\n",
                                         reply_markup=keyboard_action_repiet())


async def main_change(state: FSMContext, message: Message):
    data = await state.get_data()
    info_order: Order = await rq.get_order_id(order_id=data['order_id'])
    try:
        await message.edit_text(text=f"Плательщик: <i>"
                                     f"{data['payer_order'] if data.get('payer_order') else info_order.payer}"
                                     f"</i>\n"
                                     f"ИНН: <i>"
                                     f"{data['inn_order'] if data.get('inn_order') else info_order.inn}"
                                     f"</i>\n"
                                     f"Адрес: <i>"
                                     f"{data['address_order'] if data.get('address_order') else info_order.address}"
                                     f"</i>\n"
                                     f"Контактное лицо: <i>"
                                     f"{data['contact_order'] if data.get('contact_order') else info_order.contact}</i>\n"
                                     f"Дата доставки: <i>"
                                     f"{data['date_order'] if data.get('date_order') else info_order.date}"
                                     f"</i>\n"
                                     f"Время доставки: <i>"
                                     f"{data['time_order'] if data.get('time_order') else info_order.time}"
                                     f"</i>\n"
                                     f"Количество топлива: <i>"
                                     f"{data['volume_order'] if data.get('volume_order') else info_order.volume}"
                                     f" литров</i>\n",
                             reply_markup=keyboard_action_repiet())
    except:
        await message.answer(text=f"Плательщик: <i>"
                                  f"{data['payer_order'] if data.get('payer_order') else info_order.payer}"
                                  f"</i>\n"
                                  f"ИНН: <i>"
                                  f"{data['inn_order'] if data.get('inn_order') else info_order.inn}"
                                  f"</i>\n"
                                  f"Адрес: <i>"
                                  f"{data['address_order'] if data.get('address_order') else info_order.address}"
                                  f"</i>\n"
                                  f"Контактное лицо: <i>"
                                  f"{data['contact_order'] if data.get('contact_order') else info_order.contact}</i>\n"
                                  f"Дата доставки: <i>"
                                  f"{data['date_order'] if data.get('date_order') else info_order.date}"
                                  f"</i>\n"
                                  f"Время доставки: <i>"
                                  f"{data['time_order'] if data.get('time_order') else info_order.time}"
                                  f"</i>\n"
                                  f"Количество топлива: <i>"
                                  f"{data['volume_order'] if data.get('volume_order') else info_order.volume}"
                                  f" литров</i>\n",
                             reply_markup=keyboard_action_repiet())


@router.callback_query(F.data == 'repeatchange_volume')
async def change_order_volume(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - КОЛИЧЕСТВО ТОПЛИВА
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_volume')
    await callback.message.edit_text(text='Пришлите количество топлива')
    await state.set_state(OrderChange.volume_state)


@router.message(F.text, StateFilter(OrderChange.volume_state))
@error_handler
async def get_volume_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем количество топлива для доставки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_volume_order: {message.from_user.id}')
    volume = message.text
    if not validate_volume(volume):
        await message.answer(text='Некорректно указано количество топлива, значение должно быть числом > 0')
    else:
        volume_order = message.text
        await state.update_data(volume_order=volume_order)
        await state.set_state(state=None)
        await main_change(state=state, message=message)


@router.callback_query(F.data == 'repeatchange_address')
async def change_order_address(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - АДРЕС
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_address')
    await callback.message.edit_text(text='Пришлите адрес доставки')
    await state.set_state(OrderChange.address_state)


@router.message(F.text, StateFilter(OrderChange.address_state))
@error_handler
async def get_address_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем адрес доставки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_address_order: {message.from_user.id}')
    address_order = message.text
    await state.update_data(address_order=address_order)
    await state.set_state(state=None)
    await main_change(state=state, message=message)


@router.callback_query(F.data == 'repeatchange_payer')
async def change_order_payer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - ПЛАТЕЛЬЩИК
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_payer')
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.payer: order for order in list_orders}.values())
    if unique_orders:
        await callback.message.edit_text(text=f'Укажите название <b>ПЛАТЕЛЬЩИКА</b> заказа'
                                              f' или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[0].payer}',
                                         reply_markup=keyboards_payer(list_orders=unique_orders,
                                                                      block=0))
    else:
        await callback.message.edit_text(text=f'Пришлите название <b>ПЛАТЕЛЬЩИКА</b> заказа')
    await state.set_state(OrderChange.payer_state)


@router.callback_query(F.data.startswith('changepayerlist_'))
@error_handler
async def process_changepayerlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_changepayerlist_pagination: {callback.from_user.id}')
    block = int(callback.data.split('_')[-1])
    action = callback.data.split('_')[-2]
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.payer: order for order in list_orders}.values())
    if action == 'next':
        block += 1
    else:
        block -= 1
    if block == len(unique_orders):
        block = 0
    if block < 0:
        block = len(unique_orders) - 1
    keyboard = keyboards_payer(list_orders=unique_orders,
                               block=block)
    try:
        await callback.message.edit_text(text=f'Укажите название <b>ПЛАТИЛЬЩИКА</b>'
                                              f' заказа или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[block].payer}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Укажитe название <b>ПЛАТИЛЬЩИКА</b>'
                                              f' заказа или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[block].payer}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('changeselect_payer'))
@error_handler
async def changepayerlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор плательщика
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'changepayerlist_select: {callback.from_user.id}')
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    payer_order = info_order.payer
    await state.update_data(payer_order=payer_order)
    await state.set_state(state=None)
    await main_change(state=state, message=callback.message)


@router.message(F.text, StateFilter(OrderChange.payer_state))
@error_handler
async def process_get_input_payer(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем название плательщика и предлагаем указать ИНН
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_input_payer: {message.from_user.id}')
    payer_order = message.text
    await state.update_data(payer_order=payer_order)
    await state.set_state(state=None)
    await main_change(state=state, message=message)


@router.callback_query(F.data == 'repeatchange_inn')
async def change_order_inn(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - ИНН
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_inn')
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.inn: order for order in list_orders}.values())
    if unique_orders:
        await callback.message.edit_text(text=f'Пришлите ИНН плательщика заказа'
                                              f' или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[0].inn}',
                                         reply_markup=keyboards_inn(list_orders=unique_orders,
                                                                    block=0))
    else:
        await callback.message.edit_text(text=f'Пришлите ИНН плательщика заказа')
    await state.set_state(OrderChange.inn_state)


@router.callback_query(F.data.startswith('changeinnlist_'))
@error_handler
async def process_cahngeinnlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку ИНН заказчиков
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_cahngeinnlist_pagination: {callback.from_user.id}')
    block = int(callback.data.split('_')[-1])
    action = callback.data.split('_')[-2]
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.inn: order for order in list_orders}.values())
    if action == 'next':
        block += 1
    else:
        block -= 1
    if block == len(unique_orders):
        block = 0
    if block < 0:
        block = len(unique_orders) - 1
    keyboard = keyboards_inn(list_orders=unique_orders,
                             block=block)
    try:
        await callback.message.edit_text(text=f'Пришлите ИНН плательщика заказа'
                                              f' или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[block].inn}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Пpишлите ИНН плательщика заказа'
                                              f' или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[block].inn}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('changeselect_inn'))
@error_handler
async def changeinnlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор ИНН плательщика
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'changeinnlist_select: {callback.from_user.id}')
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    inn_order = info_order.inn
    await state.update_data(inn_order=inn_order)
    await state.set_state(state=None)
    await main_change(state=state, message=callback.message)


@router.message(F.text, StateFilter(OrderChange.inn_state))
@error_handler
async def get_inn_change(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем ИНН плательщика
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_inn_change: {message.from_user.id}')
    inn_order = message.text
    if validate_inn(inn_order):
        await state.update_data(inn_order=inn_order)
        await state.set_state(state=None)
        await main_change(state=state, message=message)
    else:
        await message.answer(text=f'ИНН введен некорректно, он должен содержать 10 цифр')


@router.callback_query(F.data == 'repeatchange_contact')
async def change_order_contact(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - КОНТАКТНОЕ ЛИЦО
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_contact')
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    list_orders: list[Order] = list(set(list_orders))
    if list_orders:
        await callback.message.edit_text(text=f'Укажите данные контактного лица на адресе доставки\n\n'
                                              f'{list_orders[0].contact}',
                                         reply_markup=keyboards_contact(list_orders=list_orders,
                                                                        block=0))
    else:
        await callback.message.edit_text(text=f'Пришлите данные контактного лица на адресе доставки')
    await state.set_state(OrderChange.contact_state)


@router.callback_query(F.data.startswith('changecontactlist_'))
@error_handler
async def process_cahngecontactlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку контактных лиц
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_cahngecontactlist_pagination: {callback.from_user.id}')
    block = int(callback.data.split('_')[-1])
    action = callback.data.split('_')[-2]
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    list_orders: list[Order] = list(set(list_orders))
    if action == 'next':
        block += 1
    else:
        block -= 1
    if block == len(list_orders):
        block = 0
    if block < 0:
        block = len(list_orders) - 1
    keyboard = keyboards_contact(list_orders=list_orders,
                                 block=block)
    try:
        await callback.message.edit_text(text=f'Укажите данные контактного лица на адресе доставки\n\n'
                                              f'{list_orders[block].contact}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Укaжите данные контактного лица на адресе доставки\n\n'
                                              f'{list_orders[block].contact}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('cahngeselect_contact'))
@error_handler
async def cahngecontactlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор контактного лица
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'cahngecontactlist_select: {callback.from_user.id}')
    try:
        await callback.message.delete()
    except:
        pass
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    contact_order = info_order.contact
    await state.update_data(contact_order=contact_order)
    await state.set_state(state=None)
    await main_change(state=state, message=callback.message)


@router.message(F.text, StateFilter(OrderChange.contact_state))
@error_handler
async def get_contact_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем данные контактного лица
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_contact_order: {message.from_user.id}')
    contact_order = message.text
    if validate_russian_phone_number(contact_order):
        await state.update_data(contact_order=contact_order)
        await state.set_state(state=None)
        await main_change(state=state, message=message)
    else:
        await message.answer(text='Номер телефона указан некорректно, формат номера: +79111111111')


@router.callback_query(F.data == 'repeatchange_date')
async def change_order_date(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - ДАТА
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_date')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.edit_text(
        "Укажите желаемую дату доставки топлива",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await state.set_state(OrderChange.date_state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(OrderChange.date_state))
async def process_simple_calendar(callback: CallbackQuery,
                                  callback_data: CallbackData,
                                  state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_select = await calendar.process_selection(callback, callback_data)
    if selected:
        current_date = datetime.now()
        date_select = date_select + timedelta(hours=14)
        if current_date < date_select:
            date_order = date_select.strftime("%d.%m.%Y")
            await state.update_data(date_order=date_order)
            await state.set_state(state=None)
            await main_change(state=state, message=callback.message)
        else:
            if current_date.day == date_select.day:
                await callback.answer(text='В день доставки заявку можно оставить до 14 часов', show_alert=True)
            else:
                await callback.answer(text='В прошлое не доставляем, выберите корректную дату', show_alert=True)
            calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
            calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
            # получаем текущую дату
            current_date = datetime.now()
            # преобразуем ее в строку
            date1 = current_date.strftime('%d/%m/%Y')
            # преобразуем дату в список
            list_date1 = date1.split('/')
            await callback.message.answer(
                "Укажите желаемую дату доставки топлива",
                reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
            )
            await state.set_state(OrderChange.date_state)
    await callback.answer()


@router.callback_query(F.data == 'repeatchange_time')
async def change_order_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обновление полей заказа - ВРЕМЯ
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_order_time')
    await callback.message.edit_text(text='Выберите удобный временной интервал для доставки',
                                     reply_markup=keyboard_time_interval())


@router.callback_query(F.data.startswith('changetimeinterval_'))
@error_handler
async def select_time_order(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Получаем время доставки
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'select_time_order: {callback.from_user.id}')
    time_order = callback.data.split('_')[-1]
    if time_order != 'other':
        await state.update_data(time_order=time_order)
        await state.set_state(state=None)
        await main_change(state=state, message=callback.message)
    else:
        await callback.message.edit_text(text='Укажите удобный временной интервал для доставки')
        await state.set_state(OrderChange.time_state)


@router.message(F.text, StateFilter(OrderChange.time_state))
@error_handler
async def get_time_state(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем желаемое время доставки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_time_state: {message.from_user.id}')
    time_order = message.text
    await state.update_data(time_order=time_order)
    await state.set_state(state=None)
    await main_change(state=state, message=message)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(OrderRepeat.date_state))
async def process_simple_calendar(callback: CallbackQuery,
                                  callback_data: CallbackData,
                                  state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_select = await calendar.process_selection(callback, callback_data)
    if selected:
        current_date = datetime.now()
        date_select = date_select + timedelta(hours=14)
        if current_date < date_select:
            date_order = date_select.strftime("%d.%m.%Y")
            await state.update_data(date_order=date_order)
            await state.set_state(state=None)
            await callback.message.edit_text(text='Выберите удобный временной интервал для доставки',
                                             reply_markup=keyboard_time_interval_r())
        else:
            if current_date.day == date_select.day:
                await callback.answer(text='В день доставки заявку можно оставить до 14 часов', show_alert=True)
            else:
                await callback.answer(text='В прошлое не доставляем, выберите корректную дату', show_alert=True)
            calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
            calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
            # получаем текущую дату
            current_date = datetime.now()
            # преобразуем ее в строку
            date1 = current_date.strftime('%d/%m/%Y')
            # преобразуем дату в список
            list_date1 = date1.split('/')
            await callback.message.answer(
                "Укажите желаемую дату доставки топлива",
                reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
            )
    await callback.answer()


@router.callback_query(F.data.startswith('rchangetimeinterval_'))
@error_handler
async def select_time_order_r(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Получаем время доставки
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'select_time_order_r: {callback.from_user.id}')
    time_order = callback.data.split('_')[-1]
    if time_order != 'other':
        await state.update_data(time_order=time_order)
        await state.set_state(state=None)
        data = await state.get_data()
        info_order: Order = await rq.get_order_id(data['order_id'])
        await callback.message.edit_text(text='Пришлите количество топлива')
        await state.set_state(OrderRepeat.volume_state)
        # await orderrepeat_confirm(callback=callback, state=state, bot=bot, data=data, info_order=info_order)
    else:
        await callback.message.edit_text(text='Укажите удобный временной интервал для доставки')
        await state.set_state(OrderRepeat.time_state)


@router.message(F.text, StateFilter(OrderRepeat.time_state))
@error_handler
async def get_time_state_r(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем желаемое время доставки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_time_state_r: {message.from_user.id}')
    time_order = message.text
    await state.update_data(time_order=time_order)
    await state.set_state(state=None)
    await message.edit_text(text='Пришлите количество топлива')
    await state.set_state(OrderRepeat.volume_state)


@router.message(F.text, StateFilter(OrderRepeat.volume_state))
@error_handler
async def get_volume_order_r(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем количество топлива для доставки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_volume_order: {message.from_user.id}')
    volume = message.text
    if not validate_volume(volume):
        await message.answer(text='Некорректно указано количество топлива, значение должно быть числом > 0')
    else:
        volume_order = message.text
        await state.update_data(volume_order=volume_order)
        await state.set_state(state=None)
        data = await state.get_data()
        info_order: Order = await rq.get_order_id(data['order_id'])
        await orderrepeat_confirm(message=message, state=state, bot=bot, data=data, info_order=info_order)


async def orderrepeat_confirm(message: Message, state: FSMContext, bot: Bot, data: dict, info_order: Order):
    logging.info('orderrepeat_confirm')
    order_data = {"tg_id": message.from_user.id,
                  "payer": data['payer_order'] if data.get('payer_order') else info_order.payer,
                  "inn": data['inn_order'] if data.get('inn_order') else info_order.inn,
                  "address": data['address_order'] if data.get('address_order') else info_order.address,
                  "contact": data['contact_order'] if data.get('contact_order') else info_order.contact,
                  "date": data['date_order'] if data.get('date_order') else info_order.date,
                  "time": data['time_order'] if data.get('time_order') else info_order.time,
                  "volume": data['volume_order'] if data.get('volume_order') else info_order.volume,
                  "status": rq.OrderStatus.create,
                  "date_create": datetime.now().strftime('%d.%m.%Y %H:%M')}
    order_id: int = await rq.add_order(data=order_data)
    await state.update_data(order_id=order_id)
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    if not list_users:
        await message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
        return
    keyboard = keyboards_executor_personal(list_users=list_users,
                                           back=0,
                                           forward=2,
                                           count=6,
                                           order_id=order_id)
    list_admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
    admins_tg_id: list[int] = [admin.tg_id for admin in list_admins]
    info_order: Order = await rq.get_order_id(order_id=order_id)
    if message.from_user.id in admins_tg_id:
        await message.answer(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}'
                                  f'Плательщик: <i>{info_order.payer}</i>\n'
                                  f'ИНН: <i>{info_order.inn}</i>\n'
                                  f'Адрес: <i>{info_order.address}</i>\n'
                                  f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                  f'Дата доставки: <i>{info_order.date}</i>\n'
                                  f'Время доставки: <i>{info_order.time}</i>\n'
                                  f'Количество топлива: <i>{info_order.volume} литров</i>\n',
                             reply_markup=keyboard)
    else:
        msg = await message.answer(text=f'Заказ № {order_id} создан и передан администратору. '
                                        f'О смене статуса заказа мы вас оповестим',
                                   reply_markup=keyboard_delete_partner(order_id=order_id))
        # добавляем информацию о сообщении в БД для последующего редактирования
        await rq.add_order_partner_delete(data={"order_id": order_id,
                                                "partner_tg_id": message.from_user.id,
                                                "message_id": msg.message_id})
        admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
        for chat_id in admins:
            try:
                msg_admin = await bot.send_message(chat_id=chat_id.tg_id,
                                                   text=f'Заказ № {order_id} создан партнером'
                                                        f' <a href="tg://user?id={message.from_user.id}">'
                                                        f'{message.from_user.username}</a>\n\n'
                                                        f'Плательщик: <i>{info_order.payer}</i>\n'
                                                        f'ИНН: <i>{info_order.inn}</i>\n'
                                                        f'Адрес: <i>{info_order.address}</i>\n'
                                                        f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                                        f'Дата доставки: <i>{info_order.date}</i>\n'
                                                        f'Время доставки: <i>{info_order.time}</i>\n'
                                                        f'Количество топлива: <i>{info_order.volume} литров</i>\n'
                                                        f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                                   reply_markup=keyboard)
                # await rq.update_order_admin_edit(order_id=order_id,
                #                                  message_id=msg_admin.message_id,
                #                                  chat_id=chat_id.tg_id)
                await rq.add_order_admin_edit(data={"order_id": order_id,
                                                    "chat_id": chat_id.tg_id,
                                                    "message_id": msg_admin.message_id})
            except:
                pass
        msg_group = await bot.send_message(chat_id=-1002691975634,
                                           text=f'Заказ № {order_id} создан партнером'
                                                f' <a href="tg://user?id={message.from_user.id}">'
                                                f'{message.from_user.username}</a>\n\n'
                                                f'Плательщик: <i>{info_order.payer}</i>\n'
                                                f'ИНН: <i>{info_order.inn}</i>\n'
                                                f'Адрес: <i>{info_order.address}</i>\n'
                                                f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                                f'Дата доставки: <i>{info_order.date}</i>\n'
                                                f'Время доставки: <i>{info_order.time}</i>\n'
                                                f'Количество топлива: <i>{info_order.volume} литров</i>\n'
                                                f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                           message_thread_id=4)
        # await rq.update_order_admin_edit(order_id=order_id,
        #                                  chat_id=-1002691975634,
        #                                  message_id=msg_group.message_id)
        await rq.add_order_admin_edit(data={"order_id": order_id,
                                            "chat_id": -1002691975634,
                                            "message_id": msg_group.message_id})
    await state.clear()
