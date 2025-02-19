from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter, or_f
from aiogram.filters.callback_data import CallbackData
import aiogram_calendar
from aiogram_calendar import get_user_locale
from filter.user_filter import IsRoleExecutor, IsRoleAdmin
from filter.admin_filter import IsSuperAdmin
from keyboards.partner import keyboard_select_order as kb
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_text

from datetime import datetime, timedelta, date
from filter.admin_filter import check_super_admin
from database import requests as rq
from database.models import Order, User
import logging

router = Router()


class StateReport(StatesGroup):
    text_report_state = State()
    photo_report = State()


# календарь
@router.message(F.text == 'Заявки', or_f(IsRoleExecutor(), IsRoleAdmin()))
@error_handler
async def process_buttons_order(message: Message, state: FSMContext):
    """
    Отслеживание выполнения заявки
    :param message:
    :param state:
    :return:
    """
    logging.info('process_buttons_order')
    await state.set_state(state=None)
    if IsRoleExecutor():
        await message.answer(text='Выберите тип заявки',
                             reply_markup=kb.keyboard_report())


@router.callback_query(F.data.startswith('order_'))
@error_handler
async def select_type_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем тип заявки
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    type_order = callback.data.split('_')[-1]
    if type_order == 'work':
        orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=callback.from_user.id,
                                                               status=rq.OrderStatus.work)
        if orders:
            info_user: User = await rq.get_user_by_id(tg_id=orders[0].tg_id)
            autor_order = f'<b>Заявка №{orders[0].id}</b>\n' \
                          f'Заявитель: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                          f'Дата заявки: {orders[0].date_create}\n' \
                          f'Срок решения: {orders[0].deadline}\n\n'
            await callback.message.edit_text(text=f'{autor_order}{orders[0].text_order}',
                                             reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                       block=0,
                                                                                       type_order='work'))
        else:
            await callback.message.edit_text(text='Нет заявок в работе')
    if type_order == 'completed':
        orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=callback.from_user.id,
                                                               status=rq.OrderStatus.completed)
        if orders:
            info_user: User = await rq.get_user_by_id(tg_id=orders[0].tg_id)
            autor_order = f'<b>Заявка №{orders[0].id}</b>\n' \
                          f'Заявитель: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                          f'Дата заявки: {orders[0].date_create}\n' \
                          f'Срок решения: {orders[0].deadline}\n' \
                          f'Дата завершения: {orders[0].date_solution}\n' \
                          f'Оценка: {orders[0].quality}\n' \
                          f'Комментарий: {orders[0].comment}'
            await callback.message.edit_text(text=f'{autor_order}{orders[0].text_order}',
                                             reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                       block=0,
                                                                                       type_order='completed'))
        else:
            await callback.message.edit_text(text='Нет завершенных заявок')
    await state.update_data(type_order=type_order)
    await callback.answer()


@router.callback_query(F.data.startswith('itemselect_'))
@error_handler
async def select_type_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем нажатие клавиши
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    type_select = callback.data.split('_')[1]
    data = await state.get_data()
    type_order = data['type_order']
    if type_select == 'select' and type_order == 'work':
        order_id: int = int(callback.data.split('_')[-1])
        await state.update_data(report_id=order_id)
        await state.update_data(photo_report=[])
        await callback.message.edit_text(text=f'Пришлите отчет о выполненной заявке №{order_id}',
                                         reply_markup=None)
        await state.update_data(photo_report=[])
        await state.set_state(StateReport.text_report_state)
        await callback.answer()
        return

    block = int(callback.data.split('_')[-1])
    if type_select == 'plus':
        block += 1
    elif type_select == 'minus':
        block -= 1

    if type_order == 'work':
        orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=callback.from_user.id,
                                                               status=rq.OrderStatus.work)
        count_item = len(orders)
        if block == count_item:
            block = 0
        elif block < 0:
            block = count_item - 1
        info_user: User = await rq.get_user_by_id(tg_id=orders[block].tg_id)
        autor_order = f'<b>Заявка №{orders[block].id}</b>\n' \
                      f'Заявитель: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                      f'Дата заявки: {orders[block].date_create}\n' \
                      f'Срок решения: {orders[block].deadline}\n\n'
        try:
            await callback.message.edit_text(text=f'{autor_order}{orders[block].text_order}',
                                             reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                       block=block,
                                                                                       type_order=type_order))
        except:
            await callback.message.edit_text(text=f'{autor_order}{orders[block].text_order}.',
                                             reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                       block=block,
                                                                                       type_order=type_order))
    elif type_order == 'completed':
        orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=callback.from_user.id,
                                                               status=rq.OrderStatus.completed)
        count_item = len(orders)
        if block == count_item:
            block = 0
        elif block < 0:
            block = count_item - 1
        info_user: User = await rq.get_user_by_id(tg_id=orders[block].tg_id)
        autor_order = f'<b>Заявка №{orders[block].id}</b>\n' \
                      f'Заявитель: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                      f'Дата заявки: {orders[block].date_create}\n' \
                      f'Срок решения: {orders[block].deadline}\n' \
                      f'Дата завершения: {orders[block].date_solution}\n' \
                      f'Оценка: {orders[block].quality}\n' \
                      f'Комментарий: {orders[block].comment}'
        try:
            await callback.message.edit_text(text=f'{autor_order}{orders[block].text_order}',
                                             reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                       block=block,
                                                                                       type_order='completed'))
        except:
            await callback.message.edit_text(text=f'{autor_order}{orders[block].text_order}.',
                                             reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                       block=block,
                                                                                       type_order='completed'))
    await state.update_data(type_order=type_order)
    await callback.answer()


@router.message(F.text, StateFilter(StateReport.text_report_state))
@router.message(F.photo, StateFilter(StateReport.photo_report))
@error_handler
async def get_text_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_text_order: {message.chat.id}')
    if message.text:
        text_order = message.text
        await state.update_data(text_report=text_order)
        await message.answer(text='Ваш отчет получен можете добавить фото',
                             reply_markup=kb.keyboard_send_report())
    elif message.photo:
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        photo_report: list = data['photo_report']
        photo_report.append(photo_id)
        await state.update_data(photo_report=photo_report)
        await message.answer(text='Ваши материалы получены можете добавить еще фото',
                             reply_markup=kb.keyboard_send_report())


@router.callback_query(F.data.startswith('send_report_'))
@error_handler
async def send_report(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'send_report: {callback.from_user.id} ')
    answer = callback.data.split('_')[-1]
    if answer == 'photo':
        await callback.message.edit_text(text='Пришлите фото к заявке',
                                         reply_markup=None)
        await state.set_state(StateReport.photo_report)
    elif answer == 'continue':

        await state.set_state(state=None)
        await callback.message.edit_text(text='Ваш отчет направлен администратору и заявителю',
                                         reply_markup=None)

        data = await state.get_data()
        report_id = data['report_id']
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        await rq.set_order_date_solution(order_id=int(report_id), date_solution=current_date)
        await rq.set_order_report(order_id=int(report_id),
                                  text_report=data['text_report'],
                                  photo_ids_report=','.join(data["photo_report"]) if data["photo_report"] else '')
        info_order: Order = await rq.get_order_id(order_id=int(report_id))
        await send_message_admins_text(bot=bot,
                                       text=f'Отчет о выполнении заявки № {report_id} от  '
                                            f'<a href="tg://user?id={info_order.executor}">исполнителя</a> получен',
                                       keyboard=None)
        if info_order.photo_ids_report:
            for photo_id in info_order.photo_ids_report.split(','):
                try:
                    await bot.send_photo(chat_id=info_order.tg_id,
                                         photo=photo_id)
                except:
                    pass
        else:
            await bot.send_message(chat_id=info_order.tg_id,
                                   text=info_order.text_report)
        await bot.send_message(chat_id=info_order.tg_id,
                               text=f'Получен отчет о выполнении вашей заявки № {report_id}',
                               reply_markup=kb.keyboard_completed_order(order_id=report_id))
    await callback.answer()

