from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f
from filter.user_filter import IsRoleExecutor, IsRoleAdmin
from keyboards.user import keyboard_select_order as kb
from keyboards.partner.keyboard_order import keyboards_executor_personal
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_text, send_message_admins_media_group

from datetime import datetime
from database import requests as rq
from database.models import Order, User
from config_data.config import Config, load_config
from filter.filter import validate_volume
import logging

router = Router()
config: Config = load_config()


class StateReport(StatesGroup):
    text_report = State()
    photo_report = State()
    photo_counter = State()
    comment_cancel = State()


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
            text_message = f'Выберите заказ\n\n' \
                           f'Заявка: <i>№{orders[0].id}</i>\n' \
                           f'Заказчик: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                           f'Плательщик: <i>{orders[0].payer}</i>\n' \
                           f'ИНН: <i>{orders[0].inn}</i>\n' \
                           f'Адрес: <i>{orders[0].address}</i>\n' \
                           f'Контактное лицо: <i>{orders[0].contact}</i>\n' \
                           f'Дата доставки: <i>{orders[0].date}</i>\n' \
                           f'Время доставки: <i>{orders[0].time}</i>\n' \
                           f'Количество топлива: <i>{orders[0].volume} литров</i>\n'
            await callback.message.edit_text(text=f'{text_message}',
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
            order = f'Выберите заказ\n\n' \
                    f'Заявка: <i>№{orders[0].id}</i>\n' \
                    f'Заказчик: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Плательщик: <i>{orders[0].payer}</i>\n' \
                    f'ИНН: <i>{orders[0].inn}</i>\n' \
                    f'Адрес: <i>{orders[0].address}</i>\n' \
                    f'Контактное лицо: <i>{orders[0].contact}</i>\n' \
                    f'Дата доставки: <i>{orders[0].date}</i>\n' \
                    f'Время доставки: <i>{orders[0].time}</i>\n' \
                    f'Количество топлива: <i>{orders[0].volume} литров</i>\n'
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

    if type_select in ['select', 'cancel']:
        order_id: int = int(callback.data.split('_')[-1])
        info_order: Order = await rq.get_order_id(order_id=order_id)
        if info_order.status == rq.OrderStatus.cancel:
            await callback.message.edit_text(text=f'Заказ №{info_order.id} отменен')
            return
        if type_select == 'select' and type_order == 'work':

            await state.update_data(order_id=order_id)
            await callback.message.edit_text(text=f'Пришлите количество отгруженного топлива №{order_id}',
                                             reply_markup=None)
            await state.set_state(StateReport.text_report)
            await callback.answer()
            return
        elif type_select == 'cancel' and type_order == 'work':
            # order_id: str = callback.data.split('_')[-1]
            await state.update_data(order_id=order_id)
            await callback.message.edit_text(text=f'Вы отказались от выполнения заказа №{order_id},'
                                                  f' укажите причину или нажмите "ПРОПУСТИТЬ"',
                                             reply_markup=kb.keyboard_pass_comment())
            await state.set_state(StateReport.comment_cancel)
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
            order = f'Выберите заказ\n\n' \
                    f'Заявка: <i>№{orders[0].id}</i>\n' \
                    f'Заказчик: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Плательщик: <i>{orders[0].payer}</i>\n' \
                    f'ИНН: <i>{orders[0].inn}</i>\n' \
                    f'Адрес: <i>{orders[0].address}</i>\n' \
                    f'Контактное лицо: <i>{orders[0].contact}</i>\n' \
                    f'Дата доставки: <i>{orders[0].date}</i>\n' \
                    f'Время доставки: <i>{orders[0].time}</i>\n' \
                    f'Количество топлива: <i>{orders[0].volume} литров</i>\n'
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
            order = f'Выберите заказ\n\n' \
                    f'Заявка: <i>№{orders[0].id}</i>\n' \
                    f'Заказчик: <a href="tg://user?id={info_user.tg_id}">{info_user.username}</a>\n' \
                    f'Плательщик: <i>{orders[0].payer}</i>\n' \
                    f'ИНН: <i>{orders[0].inn}</i>\n' \
                    f'Адрес: <i>{orders[0].address}</i>\n' \
                    f'Контактное лицо: <i>{orders[0].contact}</i>\n' \
                    f'Дата доставки: <i>{orders[0].date}</i>\n' \
                    f'Время доставки: <i>{orders[0].time}</i>\n' \
                    f'Количество топлива: <i>{orders[0].volume} литров</i>\n'
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


@router.message(F.text, StateFilter(StateReport.text_report))
@router.message(F.photo, StateFilter(StateReport.photo_report))
@router.message(F.photo, StateFilter(StateReport.photo_counter))
@error_handler
async def get_text_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_text_order: {message.from_user.id}')
    data = await state.get_data()
    if message.text:
        if validate_volume(message.text) and float(message.text) > 0:
            text_order = message.text
            await state.update_data(text_report=float(text_order))
            await message.answer(text='Ваш отчет получен добавьте фото квитанции')
            await state.set_state(StateReport.photo_report)
        else:
            await message.answer(text=f'Количество топлива указанно не корректно',
                                 reply_markup=None)
    elif message.photo:
        data = await state.get_data()
        photo_id = message.photo[-1].file_id
        state_ = await state.get_state()
        if state_ == StateReport.photo_counter:
            await send_message_admins_media_group(bot=bot,
                                                  list_ids=[photo_id],
                                                  caption=f'Показания счетчика по заказу № {data["order_id"]} от  '
                                                          f'@{message.from_user.username}')
            await message.answer(text='Показания счетчика направлены администратору')
            return
        await state.update_data(photo_report=photo_id)
        await message.answer_photo(photo=photo_id,
                                   caption=f'{data["text_report"]}\n\n'
                                           f'Ваши материалы получены можете переснять фото или отправить отчет по'
                                           f' заказу №{data["order_id"]}',
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
    await callback.message.delete()
    await callback.message.answer(text='Ваш отчет направлен администратору')
    await callback.message.answer(text='Отправьте фотографию счетчика топлива')
    await state.set_state(state=StateReport.photo_counter)
    data = await state.get_data()
    order_id = data['order_id']
    current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
    await rq.set_order_date_solution(order_id=int(order_id),
                                     date_solution=current_date)
    await rq.set_order_report(order_id=int(order_id),
                              photo_ids_report=data['photo_report'],
                              text_order=data['text_report'])
    info_order: Order = await rq.get_order_id(order_id=int(order_id))

    await send_message_admins_media_group(bot=bot,
                                          list_ids=[info_order.photo_ids_report],
                                          caption=f'Отчет о выполнении заявки № {order_id} от  '
                                                  f'@{callback.from_user.username}'
                                                  f' получен. Отгружено {info_order.text_report} литров топлива')
    if str(info_order.tg_id) not in config.tg_bot.admin_ids.split(','):
        await bot.send_photo(chat_id=info_order.tg_id,
                             photo=info_order.photo_ids_report,
                             caption=f'Отчет о выполнении заявки № {order_id} от  '
                                     f'@{callback.from_user.username}'
                                     f' получен. Отгружено {info_order.text_report} литров топлива')
    await callback.answer()


@router.message(F.text, StateFilter(StateReport.comment_cancel))
@error_handler
async def get_comment_cancel(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Изменение данных
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_comment_cancel: {message.from_user.id}')
    comment_cancel = message.text
    await message.answer(text='Данные от вас получены и переданы администраторам')
    data = await state.get_data()
    order_id = data['order_id']
    await rq.set_order_status(order_id=order_id, status=rq.OrderStatus.cancel)
    info_order: Order = await rq.get_order_id(order_id=order_id)
    info_user: User = await rq.get_user_by_id(tg_id=info_order.tg_id)
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    keyboard = keyboards_executor_personal(list_users=list_users,
                                           back=0,
                                           forward=2,
                                           count=6,
                                           order_id=order_id)
    await send_message_admins_text(bot=bot,
                                   text=f'@{message.from_user.username}'
                                        f' отказался от выполнения заказа № {order_id},'
                                        f' комментарий: {comment_cancel}\n'
                                        f'Информация о заказе № {order_id}:\n'
                                        f'Заказчик: <a href="tg://user?id={info_order.tg_id}">{info_user.username}</a>\n' 
                                        f'Плательщик: <i>{info_order.payer}</i>\n' 
                                        f'ИНН: <i>{info_order.inn}</i>\n' 
                                        f'Адрес: <i>{info_order.address}</i>\n' 
                                        f'Контактное лицо: <i>{info_order.contact}</i>\n' 
                                        f'Дата доставки: <i>{info_order.date}</i>\n' 
                                        f'Время доставки: <i>{info_order.time}</i>\n' 
                                        f'Количество топлива: <i>{info_order.volume} литров</i>\n',
                                   keyboard=keyboard)


@router.callback_query(F.data == 'pass_comment')
@error_handler
async def pass_comment(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пропуск добавления комментария
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'send_report: {callback.from_user.id} ')
    await state.set_state(state=None)
    await callback.message.edit_text(text='Данные от вас получены и переданы')
    data = await state.get_data()
    order_id = data['order_id']
    await rq.set_order_status(order_id=order_id, status=rq.OrderStatus.cancel)
    info_order: Order = await rq.get_order_id(order_id=order_id)
    info_user: User = await rq.get_user_by_id(tg_id=info_order.tg_id)
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    keyboard = keyboards_executor_personal(list_users=list_users,
                                           back=0,
                                           forward=2,
                                           count=6,
                                           order_id=order_id)
    await send_message_admins_text(bot=bot,
                                   text=f'@{callback.from_user.username}'
                                        f' отказался от выполнения заказа № {order_id},'
                                        f' комментарий: отсутствует\n'
                                        f'Информация о заказе № {order_id}:\n'
                                        f'Заказчик: <a href="tg://user?id={info_order.tg_id}">{info_user.username}</a>\n' 
                                        f'Плательщик: <i>{info_order.payer}</i>\n' 
                                        f'ИНН: <i>{info_order.inn}</i>\n' 
                                        f'Адрес: <i>{info_order.address}</i>\n' 
                                        f'Контактное лицо: <i>{info_order.contact}</i>\n' 
                                        f'Дата доставки: <i>{info_order.date}</i>\n' 
                                        f'Время доставки: <i>{info_order.time}</i>\n' 
                                        f'Количество топлива: <i>{info_order.volume} литров</i>\n',
                                   keyboard=keyboard)
    await callback.answer()
