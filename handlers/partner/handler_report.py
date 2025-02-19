from aiogram.types import CallbackQuery, Message
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter, or_f
from aiogram.filters.callback_data import CallbackData
import aiogram_calendar
from aiogram_calendar import get_user_locale
from filter.user_filter import IsRoleExecutor, IsRoleAdmin
from filter.admin_filter import IsSuperAdmin


from datetime import datetime, timedelta, date
from filter.admin_filter import check_super_admin
from database import requests as rq
from database.models import Order
import logging

router = Router()


class StateReport(StatesGroup):
    start_period = State()
    finish_period = State()


# календарь
@router.message(F.text == 'Отчет', or_f(IsRoleExecutor(), IsRoleAdmin()))
async def process_buttons_press_report(message: Message, state: FSMContext):
    """
    Паздел отчет
    :param message:
    :param state:
    :return:
    """
    logging.info('process_buttons_press_report')
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
        await callback.message.answer(text='Статистика по категории заявки, уложился ли исполнитель в срок,'
                                           ' оценка заявителя')