from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import aiogram_calendar
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ChatAction

import keyboards.partner.keyboard_order as kb
import database.requests as rq
from database.models import User, Order
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.user_filter import IsRoleUser
from filter.filter import validate_inn, validate_russian_phone_number, validate_volume
from utils.send_admins import send_message_admins_text
from filter.user_filter import check_role

import logging
from datetime import datetime, timedelta

config: Config = load_config()
router = Router()


class OrderState(StatesGroup):
    payer_state = State()
    inn_state = State()
    address_state = State()
    contact_state = State()
    date_state = State()
    time_state = State()
    volume_state = State()


@router.callback_query(F.data == 'new_order')
async def create_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Запуск процесса создания нового заказа
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.payer: order for order in list_orders}.values())
    if unique_orders:
        await callback.message.edit_text(text=f'Пришлите название <b>ПЛАТЕЛЬЩИКА</b> заказа'
                                              f' или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[0].payer}',
                                         reply_markup=kb.keyboards_payer(list_orders=unique_orders,
                                                                         block=0))
    else:
        await callback.message.edit_text(text=f'Пришлите название <b>ПЛАТЕЛЬЩИКА</b> заказа')
    await state.set_state(OrderState.payer_state)


@router.callback_query(F.data.startswith('payerlist_'))
@error_handler
async def process_payerlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_payerlist_pagination: {callback.from_user.id}')
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
    keyboard = kb.keyboards_payer(list_orders=unique_orders,
                                  block=block)
    try:
        await callback.message.edit_text(text=f'Пришлите название <b>ПЛАТИЛЬЩИКА</b>'
                                              f' заказа или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[block].payer}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Пришлитe название <b>ПЛАТИЛЬЩИКА</b>'
                                              f' заказа или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[block].payer}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('select_payer'))
@error_handler
async def payerlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор плательщика
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'payerlist_select: {callback.from_user.id}')
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    payer_order = info_order.payer
    await state.update_data(payer_order=payer_order)
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.inn: order for order in list_orders}.values())
    if unique_orders:
        await callback.message.edit_text(text=f'Пришлите ИНН плательщика заказа'
                                              f' или выберите из ранее добавленных\n\n'
                                              f'{unique_orders[0].inn}',
                                         reply_markup=kb.keyboards_inn(list_orders=unique_orders,
                                                                       block=0))
    else:
        await callback.message.answer(text=f'Пришлите ИНН плательщика заказа')
    await state.set_state(OrderState.inn_state)


@router.message(F.text, StateFilter(OrderState.payer_state))
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
    tg_id = message.from_user.id
    if await check_role(tg_id=message.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    unique_orders = list({order.inn: order for order in list_orders}.values())
    if unique_orders:
        await message.answer(text=f'Пришлите ИНН плательщика заказа'
                                  f' или выберите из ранее добавленных\n\n'
                                  f'{unique_orders[0].inn}',
                             reply_markup=kb.keyboards_inn(list_orders=unique_orders,
                                                           block=0))
    else:
        await message.answer(text=f'Пришлите ИНН плательщика заказа')
    await state.set_state(OrderState.inn_state)


@router.callback_query(F.data.startswith('innlist_'))
@error_handler
async def process_innlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку ИНН заказчиков
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_innlist_pagination: {callback.from_user.id}')
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
    keyboard = kb.keyboards_inn(list_orders=unique_orders,
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


@router.callback_query(F.data.startswith('select_inn'))
@error_handler
async def innlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор ИНН плательщика
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'innlist_select: {callback.from_user.id}')
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    inn_order = info_order.inn
    await state.update_data(inn_order=inn_order)
    await callback.message.edit_text(text=f'Пришлите адрес, на который требуется доставить топливо')
    await state.set_state(OrderState.address_state)


@router.message(F.text, StateFilter(OrderState.inn_state))
@error_handler
async def get_inn(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем ИНН плательщика
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_address_order: {message.from_user.id}')
    inn_order = message.text
    if validate_inn(inn_order):
        await state.update_data(inn_order=inn_order)
        await message.answer(text=f'Пришлите адрес, на который требуется доставить топливо')
        await state.set_state(OrderState.address_state)
    else:
        await message.answer(text=f'ИНН введен некорректно, он должен содержать 10 цифр')


@router.message(F.text, StateFilter(OrderState.address_state))
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

    tg_id = message.from_user.id
    if await check_role(tg_id=message.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders: list[Order] = await rq.get_order_tg_id(tg_id=tg_id)
    list_orders: list[Order] = list(set(list_orders))
    if list_orders:
        await message.answer(text=f'Укажите данные контактного лица на адресе доставки\n\n'
                                  f'{list_orders[0].contact}',
                             reply_markup=kb.keyboards_contact(list_orders=list_orders,
                                                               block=0))
    else:
        await message.answer(text=f'Пришлите данные контактного лица на адресе доставки')
    await state.set_state(OrderState.contact_state)


@router.callback_query(F.data.startswith('contactlist_'))
@error_handler
async def process_contactlist_pagination(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку контактных лиц
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_contactlist_pagination: {callback.from_user.id}')
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
    keyboard = kb.keyboards_contact(list_orders=list_orders,
                                    block=block)
    try:
        await callback.message.edit_text(text=f'Укажите данные контактного лица на адресе доставки\n\n'
                                              f'{list_orders[block].contact}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Укaжите данные контактного лица на адресе доставки\n\n'
                                              f'{list_orders[block].contact}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('select_contact'))
@error_handler
async def contactlist_select(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор контактного лица
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'contactlist_select: {callback.from_user.id}')
    try:
        await callback.message.delete()
    except:
        pass
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    contact_order = info_order.contact
    await state.update_data(contact_order=contact_order)
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
    await state.set_state(OrderState.date_state)


@router.message(F.text, StateFilter(OrderState.contact_state))
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
        calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
        calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        date1 = current_date.strftime('%d/%m/%Y')
        # преобразуем дату в список
        list_date1 = date1.split('/')
        await message.answer(
            "Укажите желаемую дату доставки топлива",
            reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
        )
        await state.set_state(OrderState.date_state)
    else:
        await message.answer(text='Номер телефона указан некорректно, формат номера: +79111111111')


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(OrderState.date_state))
async def process_simple_calendar(callback: CallbackQuery,
                                  callback_data: CallbackData,
                                  state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_select = await calendar.process_selection(callback, callback_data)
    if selected:
        current_date = datetime.now()
        date_select = date_select + timedelta(hours=14)
        # print(current_date.hour, current_date, date_select + timedelta(days=1))
        if current_date < date_select:
            date_order = date_select.strftime("%d.%m.%Y")
            await state.update_data(date_order=date_order)
            await callback.message.answer(text='Выберите удобный временной интервал для доставки',
                                          reply_markup=kb.keyboard_time_interval())
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
            await state.set_state(OrderState.date_state)
    await callback.answer()


@router.callback_query(F.data.startswith('timeinterval_'))
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
        await callback.message.edit_text(text=f'Пришлите количество топлива')
        await state.set_state(OrderState.volume_state)
    else:
        await callback.message.edit_text(text='Укажите удобный временной интервал для доставки')
        await state.set_state(OrderState.time_state)


@router.message(F.text, StateFilter(OrderState.time_state))
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
    await message.answer(text=f'Пришлите количество топлива')
    await state.set_state(OrderState.volume_state)


@router.message(F.text, StateFilter(OrderState.volume_state))
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
        await state.set_state(state=None)
        volume_order = message.text
        await state.update_data(volume_order=volume_order)

        list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
        if not list_users:
            await message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
            return
        data = await state.get_data()
        order_data = {"tg_id": message.from_user.id,
                      "payer": data['payer_order'],
                      "inn": data['inn_order'],
                      "address": data['address_order'],
                      "contact": data['contact_order'],
                      "date": data['date_order'],
                      "time": data['time_order'],
                      "volume": data["volume_order"],
                      "status": rq.OrderStatus.create,
                      "date_create": datetime.now().strftime('%d.%m.%Y %H:%M')}
        order_id: int = await rq.add_order(data=order_data)
        await state.update_data(order_id=order_id)
        keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                                  back=0,
                                                  forward=2,
                                                  count=6,
                                                  order_id=order_id)
        list_admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
        admins_tg_id: list[int] = [admin.tg_id for admin in list_admins]
        if message.from_user.id in admins_tg_id:
            await message.answer(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}'
                                      f'Плательщик: <i>{data["payer_order"]}</i>\n'
                                      f'ИНН: <i>{data["inn_order"]}</i>\n'
                                      f'Адрес: <i>{data["address_order"]}</i>\n'
                                      f'Контактное лицо: <i>{data["contact_order"]}</i>\n'
                                      f'Дата доставки: <i>{data["date_order"]}</i>\n'
                                      f'Время доставки: <i>{data["time_order"]}</i>\n'
                                      f'Количество топлива: <i>{data["volume_order"]} литров</i>\n',
                                 reply_markup=keyboard)
        else:
            await message.answer(text=f'Заказ № {order_id} создан и передан администратору. '
                                      f'О смене статуса заказа мы вас оповестим')
            admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
            for chat_id in admins:
                try:
                    await bot.send_message(chat_id=chat_id.tg_id,
                                           text=f'Заказ № {order_id} создан партнером'
                                                f' <a href="tg://user?id={message.from_user.id}">'
                                                f'{message.from_user.username}</a>\n\n'
                                                f'Плательщик: <i>{data["payer_order"]}</i>\n'
                                                f'ИНН: <i>{data["inn_order"]}</i>\n'
                                                f'Адрес: <i>{data["address_order"]}</i>\n'
                                                f'Контактное лицо: <i>{data["contact_order"]}</i>\n'
                                                f'Дата доставки: <i>{data["date_order"]}</i>\n'
                                                f'Время доставки: <i>{data["time_order"]}</i>\n'
                                                f'Количество топлива: <i>{data["volume_order"]} литров</i>\n'  
                                                f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                           reply_markup=keyboard)
                except:
                    pass
#
#
# @router.callback_query(F.data.startswith('executor_select_forward_'))
# @error_handler
# async def process_forward_executor(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
#     """
#     Пагинация по списку пользователей вперед
#     :param callback:
#     :param state:
#     :param bot:
#     :return:
#     """
#     logging.info(f'process_forward_executor: {callback.from_user.id}')
#     list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
#     forward = int(callback.data.split('_')[-1]) + 1
#     order_id = int(callback.data.split('_')[-2])
#     info_order: Order = await rq.get_order_id(order_id=order_id)
#     # БЛОК ПРОВЕРКИ ДОСТУПНОСТИ ЗАКАЗА К РАСПЕРЕДЕЛЕНИЮ
#     if not info_order:
#         await callback.message.edit_text(text=f'Заказ №{order_id} не найден в БД, возможно его удалили')
#         return
#     if info_order.status == rq.OrderStatus.work:
#         executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
#         await callback.message.edit_text(text=f'Заказ №{order_id} уже распределен, назначен ВОДИТЕЛЬ '
#                                               f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
#         return
#     if info_order.status == rq.OrderStatus.completed:
#         executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
#         await callback.message.edit_text(text=f'Заказ №{order_id} уже выполнен, исполнитель ВОДИТЕЛЬ '
#                                               f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
#         return
#     info_user: User = await rq.get_user_by_id(tg_id=info_order.tg_id)
#     back = forward - 2
#     keyboard = kb.keyboards_executor_personal(list_users=list_users,
#                                               back=back,
#                                               forward=forward,
#                                               count=6,
#                                               order_id=order_id)
#     try:
#         await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
#                                               f' <a href="tg://user?id={info_order.tg_id}">'
#                                               f'{info_user.username}</a>\n\n'
#                                               f'Плательщик: <i>{info_order.payer}</i>\n'
#                                               f'ИНН: <i>{info_order.inn}</i>\n'
#                                               f'Адрес: <i>{info_order.address}</i>\n'
#                                               f'Контактное лицо: <i>{info_order.contact}</i>\n'
#                                               f'Дата доставки: <i>{info_order.date}</i>\n'
#                                               f'Время доставки: <i>{info_order.time}</i>\n'
#                                               f'Количество топлива: <i>{info_order.volume} литров</i>\n'
#                                               f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
#                                          reply_markup=keyboard)
#     except:
#         await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
#                                               f' <a href="tg://user?id={info_order.tg_id}">'
#                                               f'{info_user.username}</a>\n\n'
#                                               f'Плательщик: <i>{info_order.payer}</i>\n'
#                                               f'ИНН: <i>{info_order.inn}</i>\n'
#                                               f'Адрес: <i>{info_order.address}</i>\n'
#                                               f'Контактное лицо: <i>{info_order.contact}</i>\n'
#                                               f'Дата доставки: <i>{info_order.date}</i>\n'
#                                               f'Время доставки: <i>{info_order.time}</i>\n'
#                                               f'Количество топлива: <i>{info_order.volume} литров</i>\n'
#                                               f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}.',
#                                          reply_markup=keyboard)
#
#
# @router.callback_query(F.data.startswith('executor_select_back_'))
# @error_handler
# async def process_back_executor(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
#     """
#     Пагинация по списку пользователей назад
#     :param callback:
#     :param state:
#     :param bot:
#     :return:
#     """
#     logging.info(f'process_back_executor: {callback.from_user.id}')
#     print(callback.data)
#     list_users = await rq.get_users_role(role=rq.UserRole.executor)
#     back = int(callback.data.split('_')[-1]) - 1
#     order_id = int(callback.data.split('_')[-2])
#     info_order: Order = await rq.get_order_id(order_id=order_id)
#     # БЛОК ПРОВЕРКИ ДОСТУПНОСТИ ЗАКАЗА К РАСПЕРЕДЕЛЕНИЮ
#     if not info_order:
#         await callback.message.edit_text(text=f'Заказ №{order_id} не найден в БД, возможно его удалили')
#         return
#     if info_order.status == rq.OrderStatus.work:
#         executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
#         await callback.message.edit_text(text=f'Заказ №{order_id} уже распределен, назначен ВОДИТЕЛЬ '
#                                               f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
#         return
#     if info_order.status == rq.OrderStatus.completed:
#         executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
#         await callback.message.edit_text(text=f'Заказ №{order_id} уже выполнен, исполнитель ВОДИТЕЛЬ '
#                                               f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
#         return
#     info_user: User = await rq.get_user_by_id(tg_id=info_order.tg_id)
#     forward = back + 2
#     keyboard = kb.keyboards_executor_personal(list_users=list_users,
#                                               back=back,
#                                               forward=forward,
#                                               count=6,
#                                               order_id=order_id)
#     try:
#         await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
#                                               f' <a href="tg://user?id={info_order.tg_id}">'
#                                               f'{info_user.username}</a>\n\n'
#                                               f'Плательщик: <i>{info_order.payer}</i>\n'
#                                               f'ИНН: <i>{info_order.inn}</i>\n'
#                                               f'Адрес: <i>{info_order.address}</i>\n'
#                                               f'Контактное лицо: <i>{info_order.contact}</i>\n'
#                                               f'Дата доставки: <i>{info_order.date}</i>\n'
#                                               f'Время доставки: <i>{info_order.time}</i>\n'
#                                               f'Количество топлива: <i>{info_order.volume} литров</i>\n'
#                                               f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
#                                          reply_markup=keyboard)
#     except:
#         await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
#                                               f' <a href="tg://user?id={info_order.tg_id}">'
#                                               f'{info_user.username}</a>\n\n'
#                                               f'Плательщик: <i>{info_order.payer}</i>\n'
#                                               f'ИНН: <i>{info_order.inn}</i>\n'
#                                               f'Адрес: <i>{info_order.address}</i>\n'
#                                               f'Контактное лицо: <i>{info_order.contact}</i>\n'
#                                               f'Дата доставки: <i>{info_order.date}</i>\n'
#                                               f'Время доставки: <i>{info_order.time}</i>\n'
#                                               f'Количество топлива: <i>{info_order.volume} литров</i>\n'
#                                               f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}.',
#                                          reply_markup=keyboard)
#
#
# @router.callback_query(F.data.startswith('executor_select_'))
# @error_handler
# async def process_executor_select(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
#     """
#     Обработка выбранного водителя для назначения на заказ
#     :param callback:
#     :param state:
#     :param bot:
#     :return:
#     """
#     logging.info(f'process_executor_select: {callback.from_user.id}')
#     telegram_id = int(callback.data.split('_')[-1])
#     order_id = int(callback.data.split('_')[-2])
#     info_order: Order = await rq.get_order_id(order_id=order_id)
#     # БЛОК ПРОВЕРКИ ДОСТУПНОСТИ ЗАКАЗА К РАСПЕРЕДЕЛЕНИЮ
#     if not info_order:
#         await callback.message.edit_text(text=f'Заказ №{order_id} не найден в БД, возможно его удалили')
#         return
#     if info_order.status == rq.OrderStatus.work:
#         executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
#         await callback.message.edit_text(text=f'Заказ №{order_id} уже распределен, назначен ВОДИТЕЛЬ '
#                                               f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
#         return
#     if info_order.status == rq.OrderStatus.completed:
#         executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
#         await callback.message.edit_text(text=f'Заказ №{order_id} уже выполнен, исполнитель ВОДИТЕЛЬ '
#                                               f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
#         return
#     # проверка что водитель может быть назанчен на заказ (бот может отправить ему сообщение)
#     try:
#         await bot.send_chat_action(callback.from_user.id, 'typing')
#     except:
#         await callback.answer(text='Водитель заблокировал бота или не запускал его',
#                               show_alert=True)
#         list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
#         if not list_users:
#             await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
#             return
#         keyboard = kb.keyboards_executor_personal(list_users=list_users,
#                                                   back=0,
#                                                   forward=2,
#                                                   count=6,
#                                                   order_id=order_id)
#         await callback.message.answer(text=f'Заказ № {order_id}\n\n'
#                                            f'Плательщик: <i>{info_order.payer}</i>\n'
#                                            f'ИНН: <i>{info_order.inn}</i>\n'
#                                            f'Адрес: <i>{info_order.address}</i>\n'
#                                            f'Контактное лицо: <i>{info_order.contact}</i>\n'
#                                            f'Дата доставки: <i>{info_order.date}</i>\n'
#                                            f'Время доставки: <i>{info_order.time}</i>\n'
#                                            f'Количество топлива: <i>{info_order.volume} литров</i>\n'
#                                            f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}.',
#                                       reply_markup=keyboard)
#         return
#
#     await state.update_data(tg_id_executor=telegram_id)
#     user_info: User = await rq.get_user_by_id(tg_id=telegram_id)
#     order_info: Order = await rq.get_order_id(order_id=order_id)
#     if not order_info:
#         await callback.message.delete()
#         await callback.message.answer(text='Заказ удален')
#         return
#     await state.update_data(order_id=order_id)
#     await callback.message.edit_text(text=f'Заказ  № {order_id}\n'
#                                           f'Водитель <a href="tg://user?id={user_info.tg_id}">'
#                                           f'{user_info.username}</a> назначен для доставки {order_info.volume} '
#                                           f'литров топлива на адрес {order_info.address}',
#                                      reply_markup=kb.keyboard_confirm_select_executor())
#
#
# @router.callback_query(F.data.startswith('appoint_'))
# @error_handler
# async def process_confirm_appoint(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
#     """
#     Подтверждение назначения водителя
#     :param callback:
#     :param state:
#     :param bot:
#     :return:
#     """
#     logging.info(f'process_not_del_personal_list: {callback.from_user.id}')
#     select = callback.data.split('_')[-1]
#     if select == 'cancel':
#         data = await state.get_data()
#         order_id = data["order_id"]
#         await rq.set_order_status(order_id=order_id,
#                                   status=rq.OrderStatus.cancel)
#         list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
#         if not list_users:
#             await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
#             return
#         order_info: Order = await rq.get_order_id(order_id=order_id)
#         keyboard = kb.keyboards_executor_personal(list_users=list_users,
#                                                   back=0,
#                                                   forward=2,
#                                                   count=6,
#                                                   order_id=order_id)
#         await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}\n\n'
#                                               f'Плательщик: <i>{order_info.payer}</i>\n'
#                                               f'ИНН: <i>{order_info.inn}</i>\n'
#                                               f'Адрес: <i>{order_info.address}</i>\n'
#                                               f'Контактное лицо: <i>{order_info.contact}</i>\n'
#                                               f'Дата доставки: <i>{order_info.date}</i>\n'
#                                               f'Время доставки: <i>{order_info.time}</i>\n'
#                                               f'Количество топлива: <i>{order_info.volume} литров</i>\n',
#                                          reply_markup=keyboard)
#     else:
#         data = await state.get_data()
#         order_id = data["order_id"]
#         tg_id_executor = data['tg_id_executor']
#         user_info = await rq.get_user_by_id(tg_id=tg_id_executor)
#         order_info: Order = await rq.get_order_id(order_id=order_id)
#         if not order_info:
#             await callback.message.delete()
#             await callback.message.answer(text='Заказ удален')
#             return
#         await callback.message.edit_text(text=f'Заказ № {order_id} создан.\n\n'
#                                               f'Плательщик: <i>{order_info.payer}</i>\n'
#                                               f'ИНН: <i>{order_info.inn}</i>\n'
#                                               f'Адрес: <i>{order_info.address}</i>\n'
#                                               f'Контактное лицо: <i>{order_info.contact}</i>\n'
#                                               f'Дата доставки: <i>{order_info.date}</i>\n'
#                                               f'Время доставки: <i>{order_info.time}</i>\n'
#                                               f'Количество топлива: <i>{order_info.volume} литров</i>\n'
#                                               f'Водитель <a href="tg://user?id={user_info.tg_id}">'
#                                               f'{user_info.username}</a>')
#         try:
#             await bot.send_message(chat_id=order_info.tg_id,
#                                    text=f'Заказ № {order_id} создан.\n\n'
#                                         f'Плательщик: <i>{order_info.payer}</i>\n'
#                                         f'ИНН: <i>{order_info.inn}</i>\n'
#                                         f'Адрес: <i>{order_info.address}</i>\n'
#                                         f'Контактное лицо: <i>{order_info.contact}</i>\n'
#                                         f'Дата доставки: <i>{order_info.date}</i>\n'
#                                         f'Время доставки: <i>{order_info.time}</i>\n'
#                                         f'Количество топлива: <i>{order_info.volume} литров</i>\n'
#                                         f'Водитель <a href="tg://user?id={user_info.tg_id}">'
#                                         f'{user_info.username}</a>')
#         except:
#             await callback.message.answer(text='Партнер не оповещен о назначении водителя на его заказ,'
#                                                ' возможно он заблокировал бота')
#         await rq.set_order_executor(order_id=order_id,
#                                     executor=user_info.tg_id)
#         await rq.set_order_date_create(order_id=order_id,
#                                        date_create=datetime.now().strftime('%d.%m.%Y %H:%M'))
#         await rq.set_order_status(order_id=order_id,
#                                   status=rq.OrderStatus.work)
#         try:
#             await bot.send_message(chat_id=tg_id_executor,
#                                    text=f'Заказ № {order_id}\n'
#                                         f'Плательщик: <i>{order_info.payer}</i>\n'
#                                         f'ИНН: <i>{order_info.inn}</i>\n'
#                                         f'Адрес: <i>{order_info.address}</i>\n'
#                                         f'Контактное лицо: <i>{order_info.contact}</i>\n'
#                                         f'Дата доставки: <i>{order_info.date}</i>\n'
#                                         f'Время доставки: <i>{order_info.time}</i>\n'
#                                         f'Количество топлива: <i>{order_info.volume} литров</i>\n'
#                                         f'Пришлите фото оплаченной квитанции, для этого выберите заказ в разделе "ЗАКАЗ"')
#         except:
#             await callback.message.answer(text='Водитель не оповещен о поступлении нового заказа,'
#                                                ' возможно он заблокировал или не запускал бота')
#         list_admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
#         for admin in list_admins:
#             await bot.send_message(chat_id=admin.tg_id,
#                                    text=f'На заказ №{order_id} администратором @{callback.from_user.username}'
#                                         f' назначен водитель <a href="tg://user?id={user_info.tg_id}">'
#                                         f'{user_info.username}</a>')
#     await callback.answer()
