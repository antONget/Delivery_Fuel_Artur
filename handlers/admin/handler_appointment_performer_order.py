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
from database.models import User, Order, OrderAdminEdit, OrderPartnerDelete
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.user_filter import IsRoleUser
from filter.filter import validate_inn, validate_russian_phone_number, validate_volume
from utils.send_admins import send_message_admins_text
from filter.user_filter import check_role

import logging
from datetime import datetime

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


@router.callback_query(F.data.startswith('executor_select_forward_'))
@error_handler
async def process_forward_executor(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей (водителей) вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_executor: {callback.from_user.id}')
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    forward = int(callback.data.split('_')[-1]) + 1
    order_id = int(callback.data.split('_')[-2])
    info_order: Order = await rq.get_order_id(order_id=order_id)
    # БЛОК ПРОВЕРКИ ДОСТУПНОСТИ ЗАКАЗА К РАСПЕРЕДЕЛЕНИЮ
    if not info_order:
        await callback.message.edit_text(text=f'Заказ №{order_id} не найден в БД, возможно его удалили')
        return
    if info_order.status == rq.OrderStatus.work:
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await callback.message.edit_text(text=f'Заказ №{order_id} уже распределен, назначен ВОДИТЕЛЬ '
                                              f'<a href="tg://user?id={info_order.executor}">{executor.username}</a>')
        return
    if info_order.status == rq.OrderStatus.completed:
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await callback.message.edit_text(text=f'Заказ №{order_id} уже выполнен, исполнитель ВОДИТЕЛЬ '
                                              f'<a href="tg://user?id={info_order.executor}">{executor.username}</a>')
        return
    info_user: User = await rq.get_user_by_id(tg_id=info_order.tg_id)
    back = forward - 2
    keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                              back=back,
                                              forward=forward,
                                              count=6,
                                              order_id=order_id)
    try:
        await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
                                              f' <a href="tg://user?id={info_order.tg_id}">'
                                              f'{info_user.username}</a>\n\n'
                                              f'Плательщик: <i>{info_order.payer}</i>\n'
                                              f'ИНН: <i>{info_order.inn}</i>\n'
                                              f'Адрес: <i>{info_order.address}</i>\n'
                                              f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                              f'Дата доставки: <i>{info_order.date}</i>\n'
                                              f'Время доставки: <i>{info_order.time}</i>\n'
                                              f'Количество топлива: <i>{info_order.volume} литров</i>\n'  
                                              f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
                                              f' <a href="tg://user?id={info_order.tg_id}">'
                                              f'{info_user.username}</a>\n\n'
                                              f'Плательщик: <i>{info_order.payer}</i>\n'
                                              f'ИНН: <i>{info_order.inn}</i>\n'
                                              f'Адрес: <i>{info_order.address}</i>\n'
                                              f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                              f'Дата доставки: <i>{info_order.date}</i>\n'
                                              f'Время доставки: <i>{info_order.time}</i>\n'
                                              f'Количество топлива: <i>{info_order.volume} литров</i>\n'  
                                              f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}.',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('executor_select_back_'))
@error_handler
async def process_back_executor(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей назад
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_back_executor: {callback.from_user.id}')
    # print(callback.data)
    list_users = await rq.get_users_role(role=rq.UserRole.executor)
    back = int(callback.data.split('_')[-1]) - 1
    order_id = int(callback.data.split('_')[-2])
    info_order: Order = await rq.get_order_id(order_id=order_id)
    # БЛОК ПРОВЕРКИ ДОСТУПНОСТИ ЗАКАЗА К РАСПЕРЕДЕЛЕНИЮ
    if not info_order:
        await callback.message.edit_text(text=f'Заказ №{order_id} не найден в БД, возможно его удалили')
        return
    if info_order.status == rq.OrderStatus.work:
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await callback.message.edit_text(text=f'Заказ №{order_id} уже распределен, назначен ВОДИТЕЛЬ '
                                              f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
        return
    if info_order.status == rq.OrderStatus.completed:
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await callback.message.edit_text(text=f'Заказ №{order_id} уже выполнен, исполнитель ВОДИТЕЛЬ '
                                              f'<a href="tg://user?id={info_order.executor}">{executor.username}</a')
        return
    info_user: User = await rq.get_user_by_id(tg_id=info_order.tg_id)
    forward = back + 2
    keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                              back=back,
                                              forward=forward,
                                              count=6,
                                              order_id=order_id)
    try:
        await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
                                              f' <a href="tg://user?id={info_order.tg_id}">'
                                              f'{info_user.username}</a>\n\n'
                                              f'Плательщик: <i>{info_order.payer}</i>\n'
                                              f'ИНН: <i>{info_order.inn}</i>\n'
                                              f'Адрес: <i>{info_order.address}</i>\n'
                                              f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                              f'Дата доставки: <i>{info_order.date}</i>\n'
                                              f'Время доставки: <i>{info_order.time}</i>\n'
                                              f'Количество топлива: <i>{info_order.volume} литров</i>\n'  
                                              f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером'
                                              f' <a href="tg://user?id={info_order.tg_id}">'
                                              f'{info_user.username}</a>\n\n'
                                              f'Плательщик: <i>{info_order.payer}</i>\n'
                                              f'ИНН: <i>{info_order.inn}</i>\n'
                                              f'Адрес: <i>{info_order.address}</i>\n'
                                              f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                              f'Дата доставки: <i>{info_order.date}</i>\n'
                                              f'Время доставки: <i>{info_order.time}</i>\n'
                                              f'Количество топлива: <i>{info_order.volume} литров</i>\n'  
                                              f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}.',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('executor_select_'))
@error_handler
async def process_executor_select(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Обработка выбранного водителя для назначения на заказ
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_executor_select:{callback.data} {callback.from_user.id}')
    telegram_id = int(callback.data.split('_')[-1])
    order_id = int(callback.data.split('_')[-2])
    info_order: Order = await rq.get_order_id(order_id=order_id)
    # БЛОК ПРОВЕРКИ ДОСТУПНОСТИ ЗАКАЗА К РАСПЕРЕДЕЛЕНИЮ
    if not info_order:
        await callback.message.edit_text(text=f'Заказ №{order_id} не найден в БД, возможно его удалили')
        return
    if info_order.status == rq.OrderStatus.work:
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await callback.message.edit_text(text=f'Заказ №{order_id} уже распределен, назначен ВОДИТЕЛЬ '
                                              f'<a href="tg://user?id={info_order.executor}">{executor.username}</a>')
        return
    if info_order.status == rq.OrderStatus.completed:
        executor: User = await rq.get_user_by_id(tg_id=info_order.executor)
        await callback.message.edit_text(text=f'Заказ №{order_id} уже выполнен, исполнитель ВОДИТЕЛЬ '
                                              f'<a href="tg://user?id={info_order.executor}">{executor.username}</a>')
        return
    # проверка что, водитель может быть назначен на заказ (бот может отправить ему сообщение)
    try:
        await bot.send_chat_action(callback.from_user.id, 'typing')
    except:
        await callback.answer(text='Водитель заблокировал бота или не запускал его',
                              show_alert=True)
        list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
        if not list_users:
            await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
            return
        keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                                  back=0,
                                                  forward=2,
                                                  count=6,
                                                  order_id=order_id)
        await callback.message.answer(text=f'Заказ № {order_id}\n\n'
                                           f'Плательщик: <i>{info_order.payer}</i>\n'
                                           f'ИНН: <i>{info_order.inn}</i>\n'
                                           f'Адрес: <i>{info_order.address}</i>\n'
                                           f'Контактное лицо: <i>{info_order.contact}</i>\n'
                                           f'Дата доставки: <i>{info_order.date}</i>\n'
                                           f'Время доставки: <i>{info_order.time}</i>\n'
                                           f'Количество топлива: <i>{info_order.volume} литров</i>\n'  
                                           f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}.',
                                      reply_markup=keyboard)
        return

    await state.update_data(tg_id_executor=telegram_id)
    user_info: User = await rq.get_user_by_id(tg_id=telegram_id)
    order_info: Order = await rq.get_order_id(order_id=order_id)
    if not order_info:
        await callback.message.delete()
        await callback.message.answer(text='Заказ удален')
        return
    await state.update_data(order_id=order_id)
    await callback.message.edit_text(text=f'Заказ  № {order_id}\n'
                                          f'Водитель <a href="tg://user?id={user_info.tg_id}">'
                                          f'{user_info.username}</a> назначен для доставки {order_info.volume} '
                                          f'литров топлива на адрес {order_info.address}',
                                     reply_markup=kb.keyboard_confirm_select_executor())


@router.callback_query(F.data.startswith('appoint_'))
@error_handler
async def process_confirm_appoint(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение или отмена назначения водителя
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'Подтверждение или отмена назначения водителя: {callback.data} {callback.from_user.id}')
    data = await state.get_data()
    order_id = data["order_id"]
    logging.info(f"Номер заказа: {order_id}")
    select = callback.data.split('_')[-1]
    if select == 'cancel':
        data = await state.get_data()
        order_id = data["order_id"]
        await rq.set_order_status(order_id=order_id,
                                  status=rq.OrderStatus.cancel)
        list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
        if not list_users:
            await callback.message.answer(text=f'Нет ВОДИТЕЛЕЙ для назначения их на заказ. Добавьте водителей.')
            return
        order_info: Order = await rq.get_order_id(order_id=order_id)
        keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                                  back=0,
                                                  forward=2,
                                                  count=6,
                                                  order_id=order_id)
        await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}\n\n'
                                              f'Плательщик: <i>{order_info.payer}</i>\n'
                                              f'ИНН: <i>{order_info.inn}</i>\n'
                                              f'Адрес: <i>{order_info.address}</i>\n'
                                              f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                              f'Дата доставки: <i>{order_info.date}</i>\n'
                                              f'Время доставки: <i>{order_info.time}</i>\n'
                                              f'Количество топлива: <i>{order_info.volume} литров</i>\n',
                                         reply_markup=keyboard)
    else:
        # подтверждение назначения водителя
        data = await state.get_data()
        order_id = data["order_id"]
        tg_id_executor = data['tg_id_executor']
        user_info = await rq.get_user_by_id(tg_id=tg_id_executor)
        order_info: Order = await rq.get_order_id(order_id=order_id)
        partner_info: User = await rq.get_user_by_id(tg_id=order_info.tg_id)
        if not order_info:
            await callback.message.delete()
            await callback.message.answer(text='Заказ удален')
            return
        # обновляем сообщение у администратора назначившего водителя
        try:
            await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером <a href="tg://user?id={partner_info.tg_id}">'
                                                  f'{partner_info.username}</a>.\n\n'
                                                  f'Плательщик: <i>{order_info.payer}</i>\n'
                                                  f'ИНН: <i>{order_info.inn}</i>\n'
                                                  f'Адрес: <i>{order_info.address}</i>\n'
                                                  f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                                  f'Дата доставки: <i>{order_info.date}</i>\n'
                                                  f'Время доставки: <i>{order_info.time}</i>\n'
                                                  f'Количество топлива: <i>{order_info.volume} литров</i>\n'
                                                  f'Водитель <a href="tg://user?id={user_info.tg_id}">'
                                                  f'{user_info.username}</a>',
                                             reply_markup=None)
        except:
            await callback.message.edit_text(text=f'Заказ № {order_id} создан партнером <a href="tg://user?id={partner_info.tg_id}">'
                                                  f'{partner_info.username}</a>.\n\n'
                                                  f'Плательщик: <i>{order_info.payer}</i>\n'
                                                  f'ИНН: <i>{order_info.inn}</i>\n'
                                                  f'Адрес: <i>{order_info.address}</i>\n'
                                                  f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                                  f'Дата доставки: <i>{order_info.date}</i>\n'
                                                  f'Время доставки: <i>{order_info.time}</i>\n'
                                                  f'Количество топлива: <i>{order_info.volume} литров</i>\n'
                                                  f'Водитель <a href="tg://user?id={user_info.tg_id}">'
                                                  f'{user_info.username}</a>.',
                                             reply_markup=None)
        try:
            msg_partner: OrderPartnerDelete = await rq.get_order_partner_delete(order_id=order_id)
            msgs_admin: list[OrderAdminEdit] = await rq.get_order_admin_edit(order_id=order_id)
            msg_group = [msg for msg in msgs_admin if msg.chat_id == -1002691975634]
            try:
                # print(msg_group[0].message_id)
                await bot.edit_message_text(chat_id=-1002691975634,
                                            message_id=msg_group[0].message_id,
                                            text=f'Заказ № {order_id} создан партнером <a href="tg://user?id={partner_info.tg_id}">'
                                                 f'{partner_info.username}</a>.\n\n'
                                                 f'Плательщик: <i>{order_info.payer}</i>\n'
                                                 f'ИНН: <i>{order_info.inn}</i>\n'
                                                 f'Адрес: <i>{order_info.address}</i>\n'
                                                 f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                                 f'Дата доставки: <i>{order_info.date}</i>\n'
                                                 f'Время доставки: <i>{order_info.time}</i>\n'
                                                 f'Количество топлива: <i>{order_info.volume} литров</i>\n'
                                                 f'Назначен водитель <a href="tg://user?id={user_info.tg_id}">'
                                                 f'{user_info.username}</a>')
            except:
                pass
            try:
                msg_partner = await bot.edit_message_text(chat_id=order_info.tg_id,
                                                          message_id=msg_partner.message_id,
                                                          text=f'Заказ № {order_id} создан партнером <a href="tg://user?id={partner_info.tg_id}">'
                                                               f'{partner_info.username}</a>.\n\n'
                                                               f'Плательщик: <i>{order_info.payer}</i>\n'
                                                               f'ИНН: <i>{order_info.inn}</i>\n'
                                                               f'Адрес: <i>{order_info.address}</i>\n'
                                                               f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                                               f'Дата доставки: <i>{order_info.date}</i>\n'
                                                               f'Время доставки: <i>{order_info.time}</i>\n'
                                                               f'Количество топлива: <i>{order_info.volume} литров</i>\n'
                                                               f'Назначен водитель <a href="tg://user?id={user_info.tg_id}">'
                                                               f'{user_info.username}</a>',
                                                          reply_markup=kb.keyboard_delete_message_partner(order_id=order_id))
                await rq.update_order_partner_delete(order_id=order_id,
                                                     message_id=msg_partner.message_id)
            except:
                msg_partner = await bot.send_message(chat_id=order_info.tg_id,
                                                     text=f'Заказ № {order_id} создан партнером <a href="tg://user?id={partner_info.tg_id}">'
                                                          f'{partner_info.username}</a>.\n\n'
                                                          f'Плательщик: <i>{order_info.payer}</i>\n'
                                                          f'ИНН: <i>{order_info.inn}</i>\n'
                                                          f'Адрес: <i>{order_info.address}</i>\n'
                                                          f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                                          f'Дата доставки: <i>{order_info.date}</i>\n'
                                                          f'Время доставки: <i>{order_info.time}</i>\n'
                                                          f'Количество топлива: <i>{order_info.volume} литров</i>\n'
                                                          f'Назначен водитель <a href="tg://user?id={user_info.tg_id}">'
                                                          f'{user_info.username}</a>',
                                                     reply_markup=kb.keyboard_delete_message_partner(
                                                         order_id=order_id))
                await rq.update_order_partner_delete(order_id=order_id,
                                                     message_id=msg_partner.message_id)
        except:
            await callback.message.answer(text='Партнер не оповещен о назначении водителя на его заказ,'
                                               ' возможно он заблокировал бота')
        await rq.set_order_executor(order_id=order_id,
                                    executor=user_info.tg_id)
        await rq.set_order_date_create(order_id=order_id,
                                       date_create=datetime.now().strftime('%d.%m.%Y %H:%M'))
        await rq.set_order_status(order_id=order_id,
                                  status=rq.OrderStatus.work)
        try:
            await bot.send_message(chat_id=tg_id_executor,
                                   text=f'Заказ № {order_id}\n'
                                        f'Плательщик: <i>{order_info.payer}</i>\n'
                                        f'ИНН: <i>{order_info.inn}</i>\n'
                                        f'Адрес: <i>{order_info.address}</i>\n'
                                        f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                        f'Дата доставки: <i>{order_info.date}</i>\n'
                                        f'Время доставки: <i>{order_info.time}</i>\n'
                                        f'Количество топлива: <i>{order_info.volume} литров</i>\n'  
                                        f'Пришлите фото оплаченной квитанции, для этого выберите заказ в разделе "ЗАКАЗ"')
        except:
            await callback.message.answer(text='Водитель не оповещен о поступлении нового заказа,'
                                               ' возможно он заблокировал или не запускал бота')
        list_admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
        for admin in list_admins:
            try:
                await bot.send_message(chat_id=admin.tg_id,
                                       text=f'На заказ №{order_id} администратором @{callback.from_user.username}'
                                            f' назначен водитель <a href="tg://user?id={user_info.tg_id}">'
                                            f'{user_info.username}</a>')
                # await bot.send_message(chat_id=-1002691975634,
                #                        text=f'На заказ №{order_id} администратором @{callback.from_user.username}'
                #                             f' назначен водитель <a href="tg://user?id={user_info.tg_id}">'
                #                             f'{user_info.username}</a>',
                #                        message_thread_id=4)
            except:
                pass
        messages_admin: list[OrderAdminEdit] = await rq.get_order_admin_edit(order_id=order_id)
        for info_message_admin in messages_admin:
            try:
                await bot.edit_message_reply_markup(chat_id=info_message_admin.chat_id,
                                                    message_id=info_message_admin.message_id,
                                                    reply_markup=None)
            except:
                await bot.send_message(chat_id=config.tg_bot.support_id,
                                       text=f'Заказ № {order_id}.\n'
                                            f'Администратор {info_message_admin.chat_id}.\n'
                                            f'Ошибка при обновлении сообщения при назначении водителя')
    await callback.answer()
