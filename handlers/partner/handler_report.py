from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter, or_f
from aiogram.filters.callback_data import CallbackData
import aiogram_calendar
from aiogram_calendar import get_user_locale
from filter.user_filter import IsRoleUser
from filter.admin_filter import IsSuperAdmin

from keyboards.partner.keyboard_report import keyboard_report_admin, keyboards_report_item_one, keyboard_report_executor
from datetime import datetime, timedelta, date
from filter.user_filter import check_role
from database import requests as rq
from database.models import Order, User
import logging

router = Router()


class StateReport(StatesGroup):
    start_period = State()
    finish_period = State()


# календарь
@router.message(F.text == 'Отчет', ~IsRoleUser())
async def process_buttons_press_report(message: Message, state: FSMContext):
    """
    Раздел отчет
    :param message:
    :param state:
    :return:
    """
    logging.info('process_buttons_press_report')
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if user.role == rq.UserRole.admin:
        await message.answer(text='Выберите раздел',
                             reply_markup=keyboard_report_executor())
    else:
        await state.set_state(state=None)
        calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
        calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        date1 = current_date.strftime('%d/%m/%Y')
        # преобразуем дату в список
        list_date1 = date1.split('/')
        await message.answer(
            "Выберите начало периода получения отчета",
            reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
        )
        await state.set_state(StateReport.start_period)


@router.callback_query(F.data == 'report_period')
async def report_period(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(state=None)
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.edit_text(
        "Выберите начало периода получения отчета",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await state.set_state(StateReport.start_period)


async def process_buttons_press_finish(callback: CallbackQuery, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.edit_text(
        "Выберите конец периода получения отчета",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await callback.answer()
    await state.set_state(StateReport.finish_period)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(StateReport.start_period))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData,
                                        state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_start = await calendar.process_selection(callback_query, callback_data)
    if selected:
        # await callback_query.message.edit_text(
        #     f'Начало периода {date.strftime("%d-%m-%Y")}')
        await state.update_data(start_period=date_start)
        await process_buttons_press_finish(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(StateReport.finish_period))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_finish = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.update_data(finish_period=date_finish)
        await state.set_state(state=None)
        data = await state.get_data()
        if not await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
            quantity, volume = await rq.get_order_report(tg_id=callback.from_user.id,
                                                         data_1=data["start_period"],
                                                         data_2=data["finish_period"])
            await callback.message.answer(text=f'В период {data["start_period"].strftime("%d.%m.%Y")} -'
                                               f' {data["finish_period"].strftime("%d.%m.%Y")}\n\n'
                                               f'Выполнено заказов: {quantity}\n'
                                               f'Доставлено топлива: {volume}')
        else:
            await callback.message.answer(text="Выберите тип отчета",
                                          reply_markup=keyboard_report_admin())
    await callback.answer()


@router.callback_query(F.data == 'report_general')
async def report_general(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('report_general')
    data = await state.get_data()
    quantity_total, volume_total, list_orders = await rq.get_order_report_admin(data_1=data["start_period"],
                                                                                data_2=data["finish_period"])
    partner_dict = {}
    for order in list_orders:
        info_partner: User = await rq.get_user_by_id(tg_id=order.tg_id)
        if not partner_dict.get(info_partner.tg_id, False):
            partner_dict[info_partner.tg_id] = {"quantity": 1,
                                                "volume": order.volume}
        else:
            partner_dict[info_partner.tg_id]["quantity"] += 1
            partner_dict[info_partner.tg_id]["volume"] += order.volume
    text = f'В период {data["start_period"].strftime("%d.%m.%Y")} - ' \
           f'{data["finish_period"].strftime("%d.%m.%Y")}:\n\n'
    count = 0
    for k, v in partner_dict.items():
        count += 1
        info_partner: User = await rq.get_user_by_id(tg_id=k)
        text += f'<b>{count}. {info_partner.username}:</b>\n' \
                f'   количество отгруженного топлива: {partner_dict[k]["volume"]}\n' \
                f'   количество заказов: {partner_dict[k]["quantity"]}\n\n'
    text += f'Итого:\n' \
            f'количество отгруженного топлива: {volume_total}\n' \
            f'количество заказов: {quantity_total}'
    await callback.message.edit_text(text=text)


@router.callback_query(F.data == 'report_partner')
async def report_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('report_partner')
    await callback.message.delete()
    data = await state.get_data()
    quantity_total, volume_total, orders = await rq.get_order_report_admin(data_1=data["start_period"],
                                                                           data_2=data["finish_period"])
    if len(orders):
        info_user: User = await rq.get_user_by_id(tg_id=orders[0].tg_id)
        order = f'<b>Заявка №{orders[0].id}</b>\n' \
                f'Заказчик: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                f'Плательщик: <i>{orders[0].payer}</i>\n' \
                f'ИНН: <i> {orders[0].inn if orders[0].inn else "не указано"} </i>\n' \
                f'Адрес: <i>{orders[0].address}</i>\n' \
                f'Контактное лицо: <i>{orders[0].contact}</i>\n' \
                f'Дата доставки: <i>{orders[0].date if orders[0].date else "не указано"}</i>\n' \
                f'Время доставки: <i>{orders[0].time}</i>\n' \
                f'Количество топлива: <i>{orders[0].volume} литров</i>\n'
        print(order)
        photo_order = orders[0].photo_ids_report
        await callback.message.answer_photo(photo=photo_order,
                                            caption=f'{order}',
                                            reply_markup=keyboards_report_item_one(list_item=orders,
                                                                                   block=0))
    else:
        await callback.message.answer(text=f'В период {data["start_period"].strftime("%d.%m.%Y")} - '
                                           f'{data["finish_period"].strftime("%d.%m.%Y")} нет отчетов')


@router.callback_query(F.data.startswith('itemreport_'))
async def report_itemreport(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('report_itemreport')
    type_select = callback.data.split('_')[1]
    data = await state.get_data()
    block = int(callback.data.split('_')[-1])

    quantity_total, volume_total, orders = await rq.get_order_report_admin(data_1=data["start_period"],
                                                                           data_2=data["finish_period"])
    if type_select == 'plus':
        block += 1
        if block == len(orders):
            block = 0
    elif type_select == 'minus':
        block -= 1
        if block < 0:
            block = len(orders) - 1
    info_user: User = await rq.get_user_by_id(tg_id=orders[block].tg_id)
    order = f'<b>Заявка №{orders[block].id}</b>\n' \
            f'Заказчик: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
            f'Плательщик: <i>{orders[block].payer}</i>\n' \
            f'Адрес: <i>{orders[block].address}</i>\n' \
            f'Контактное лицо: <i>{orders[block].contact}</i>\n' \
            f'Время доставки: <i>{orders[block].time}</i>\n' \
            f'Количество топлива: <i>{orders[block].volume} литров</i>\n'
    photo_order = orders[block].photo_ids_report
    try:
        await callback.message.edit_media(media=InputMediaPhoto(media=photo_order,
                                                                caption=f'{order}'),
                                          reply_markup=keyboards_report_item_one(list_item=orders,
                                                                                 block=block))
    except:
        await callback.message.edit_media(media=InputMediaPhoto(media=photo_order,
                                                                caption=f'{order}.'),
                                          reply_markup=keyboards_report_item_one(list_item=orders,
                                                                                 block=block))