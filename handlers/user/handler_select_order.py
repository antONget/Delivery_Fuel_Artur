from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f
from filter.user_filter import IsRoleExecutor, IsRoleAdmin
from keyboards.user import keyboard_select_order as kb
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_text, send_message_admins_media_group

from datetime import datetime
from database import requests as rq
from database.models import Order, User
from config_data.config import Config, load_config
import logging

router = Router()
config: Config = load_config()


class StateReport(StatesGroup):
    text_report_state = State()
    photo_report = State()


# календарь
@router.message(F.text == 'Заказ', or_f(IsRoleExecutor(), IsRoleAdmin()))
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
            order = f'<b>Заявка №{orders[0].id}</b>\n' \
                    f'Админ: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Адрес: {orders[0].address}\n' \
                    f'Количество топлива: {orders[0].volume} литров\n'
            await callback.message.edit_text(text=f'{order}',
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
            order = f'<b>Заявка №{orders[0].id}</b>\n' \
                    f'Админ: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Адрес: {orders[0].address}\n' \
                    f'Количество топлива: {orders[0].volume} литров\n'
            photo_order = orders[0].photo_ids_report
            await callback.message.answer_photo(photo=photo_order,
                                                caption=f'{order}',
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
        await state.update_data(order_id=order_id)
        await state.update_data(photo_report=[])
        await callback.message.edit_text(text=f'Пришлите фото квитанции по заказу №{order_id}',
                                         reply_markup=None)
        await state.update_data(photo_report=[])
        await state.set_state(StateReport.photo_report)
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
        if orders:
            count_item = len(orders)
            if block == count_item:
                block = 0
            elif block < 0:
                block = count_item - 1
            info_user: User = await rq.get_user_by_id(tg_id=orders[block].tg_id)
            order = f'<b>Заявка №{orders[block].id}</b>\n' \
                    f'Админ: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Адрес: {orders[block].address}\n' \
                    f'Количество топлива: {orders[block].volume} литров'
            try:
                await callback.message.edit_text(text=f'{order}',
                                                 reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                           block=block,
                                                                                           type_order='work'))
            except:
                await callback.message.edit_text(text=f'{order}.',
                                                 reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                           block=block,
                                                                                           type_order='work'))
        else:
            await callback.message.edit_text(text='Нет заявок в работе')
    if type_order == 'completed':
        orders: list[Order] = await rq.get_orders_tg_id_status(tg_id_executor=callback.from_user.id,
                                                               status=rq.OrderStatus.completed)
        if orders:
            count_item = len(orders)
            if block == count_item:
                block = 0
            elif block < 0:
                block = count_item - 1
            info_user: User = await rq.get_user_by_id(tg_id=orders[block].tg_id)
            order = f'<b>Заявка №{orders[block].id}</b>\n' \
                    f'Админ: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Адрес: {orders[block].address}\n' \
                    f'Количество топлива: {orders[block].volume} литров'
            photo_order = orders[block].photo_ids_report
            try:
                await callback.message.edit_media(media=InputMediaPhoto(media=photo_order,
                                                                        caption=f'{order}'),
                                                  reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                            block=block,
                                                                                            type_order='completed'))
            except:
                await callback.message.edit_media(media=InputMediaPhoto(media=photo_order,
                                                                        caption=f'{order}.'),
                                                  reply_markup=kb.keyboards_select_item_one(list_item=orders,
                                                                                            block=block,
                                                                                            type_order='completed'))
        else:
            await callback.message.edit_text(text='Нет завершенных заявок')


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
        await state.update_data(photo_report=photo_id)
        await message.answer(text='Ваши материалы получены можете переснять фото или отправить отчет',
                             reply_markup=kb.keyboard_send_report())


@router.callback_query(F.data == 'send_report_continue')
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

    await state.set_state(state=None)
    await callback.message.edit_text(text='Ваш отчет направлен администратору',
                                     reply_markup=None)

    data = await state.get_data()
    order_id = data['order_id']
    current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
    await rq.set_order_date_solution(order_id=int(order_id),
                                     date_solution=current_date)
    await rq.set_order_report(order_id=int(order_id),
                              photo_ids_report=data['photo_report'])
    info_order: Order = await rq.get_order_id(order_id=int(order_id))

    await send_message_admins_media_group(bot=bot,
                                          list_ids=[info_order.photo_ids_report],
                                          caption=f'Отчет о выполнении заявки № {order_id} от  '
                                                  f'<a href="tg://user?id={info_order.executor}">ВОДИТЕЛЯ</a>'
                                                  f' получен')
    if info_order.tg_id not in config.tg_bot.admin_ids.split(','):
        await bot.send_photo(chat_id=info_order.tg_id,
                             photo=info_order.photo_ids_report,
                             caption=f'Отчет о выполнении заявки № {order_id} от  '
                                     f'<a href="tg://user?id={info_order.executor}">ВОДИТЕЛЯ</a>'
                                     f' получен')
    await callback.answer()

