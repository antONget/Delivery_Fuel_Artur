from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

import keyboards.partner.keyboard_order as kb
import database.requests as rq
from database.models import User, Order
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from filter.user_filter import IsRoleUser
from utils.send_admins import send_message_admins_text
from filter.user_filter import check_role

import logging
from datetime import datetime

config: Config = load_config()
router = Router()


class OrderState(StatesGroup):
    payer_state = State()
    address_state = State()
    contact_state = State()
    time_state = State()
    volume_state = State()


@router.message(F.text == 'Создать заказ', ~IsRoleUser())
@error_handler
async def press_button_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Запуск процедуры создания заказа
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'press_button_order: {message.chat.id}')
    tg_id = message.from_user.id
    if await check_role(tg_id=message.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders = await rq.get_order_tg_id(tg_id=tg_id)
    if list_orders:
        await message.answer(text=f'Пришлите  инн и название <b>ПЛАТЕЛЬЩИКА</b> заказа'
                                  f' или выберите из ранее добавленных\n\n'
                                  f'{list_orders[0].payer}',
                             reply_markup=kb.keyboards_payer(list_orders=list_orders,
                                                             block=0))
    else:
        await message.answer(text=f'Пришлите инн и название <b>ПЛАТЕЛЬЩИКА</b> заказа')
    await state.set_state(OrderState.payer_state)


@router.callback_query(F.data.startswith('payerlist_'))
@error_handler
async def process_forward_del_admin(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_del_admin: {callback.message.chat.id}')
    block = int(callback.data.split('_')[-1])
    action = callback.data.split('_')[-2]
    tg_id = callback.from_user.id
    if await check_role(tg_id=callback.from_user.id, role=rq.UserRole.admin):
        tg_id = None
    list_orders = await rq.get_order_tg_id(tg_id=tg_id)
    if action == 'next':
        block += 1
    else:
        block -= 1
    if block == len(list_orders):
        block = 0
    if block < 0:
        block = len(list_orders) - 1
    keyboard = kb.keyboards_payer(list_orders=list_orders,
                                  block=block)
    try:
        await callback.message.edit_text(text=f'Пришлите инн и название <b>ПЛАТИЛЬЩИКА</b>'
                                              f' заказа или выберите из ранее добавленных\n\n'
                                              f'{list_orders[block].payer}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Пришлитe инн и название <b>ПЛАТИЛЬЩИКА</b>'
                                              f' заказа или выберите из ранее добавленных\n\n'
                                              f'{list_orders[block].payer}',
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
    logging.info(f'payerlist_select: {callback.message.chat.id}')
    order_id = callback.data.split('_')[-1]
    info_order = await rq.get_order_id(int(order_id))
    payer_order = info_order.payer
    await state.update_data(payer_order=payer_order)
    await callback.message.edit_text(text=f'Пришлите адрес, на который требуется доставить топливо')
    await state.set_state(OrderState.address_state)


@router.message(F.text, StateFilter(OrderState.payer_state))
@error_handler
async def get_payer(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем данные плательщика
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_address_order: {message.chat.id}')
    payer_order = message.text
    await state.update_data(payer_order=payer_order)
    await message.answer(text=f'Пришлите адрес, на который требуется доставить топливо')
    await state.set_state(OrderState.address_state)


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
    logging.info(f'get_address_order: {message.chat.id}')
    address_order = message.text
    await state.update_data(address_order=address_order)
    await message.answer(text=f'Пришлите данные контактного лица на адресе доставки')
    await state.set_state(OrderState.contact_state)


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
    logging.info(f'get_contact_order: {message.chat.id}')
    contact_order = message.text
    await state.update_data(contact_order=contact_order)
    await message.answer(text=f'Пришлите желаемую дату и время доставки')
    await state.set_state(OrderState.time_state)


@router.message(F.text, StateFilter(OrderState.time_state))
@error_handler
async def get_time_order(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем время доставки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_time_order: {message.chat.id}')
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
    if not message.text.isdigit():
        await message.answer(text='Некорректно указано количество топлива, значение должно быть целым числом > 0')
    elif int(message.text) <= 0:
        await message.answer(text='Некорректно указано количество топлива, значение должно быть целым числом > 0')
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
                      "address": data['address_order'],
                      "contact": data['contact_order'],
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
        if str(message.from_user.id) in config.tg_bot.admin_ids.split(','):
            await message.answer(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                 reply_markup=keyboard)
        else:
            await message.answer(text=f'Заказ № {order_id} создан и передан администратору. '
                                      f'О смене статуса заказа мы вас оповестим')
            await send_message_admins_text(bot=bot,
                                           text=f'Заказ № {order_id} создан партнером'
                                                f' <a href="tg://user?id={message.from_user.id}">'
                                                f'{message.from_user.username}</a>\n\n'
                                                f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                           keyboard=keyboard)


@router.callback_query(F.data.startswith('executor_select_forward_'))
@error_handler
async def process_forward_executor(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку пользователей вперед
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_executor: {callback.message.chat.id}')
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.executor)
    forward = int(callback.data.split('_')[-1]) + 1
    order_id = int(callback.data.split('_')[-2])
    back = forward - 2
    keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                              back=back,
                                              forward=forward,
                                              count=6,
                                              order_id=order_id)
    try:
        await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Выберитe ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
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
    logging.info(f'process_back_executor: {callback.message.chat.id}')
    list_users = await rq.get_users_role(role=rq.UserRole.executor)
    back = int(callback.data.split('_')[3]) - 1
    order_id = int(callback.data.split('_')[-2])
    forward = back + 2
    keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                              back=back,
                                              forward=forward,
                                              count=6,
                                              order_id=order_id)
    try:
        await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'Выберитe ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('executor_select_'))
@error_handler
async def process_delete_user(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение удаления
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_delete_user: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[-1])
    order_id = int(callback.data.split('_')[-2])
    await state.update_data(tg_id_executor=telegram_id)
    user_info: User = await rq.get_user_by_id(tg_id=telegram_id)
    order_info: Order = await rq.get_order_id(order_id=order_id)
    await state.update_data(order_id=order_id)
    await callback.message.edit_text(text=f'Заказ  № {order_id}\n'
                                          f'Водитель <a href="tg://user?id={user_info.tg_id}">'
                                          f'{user_info.username}</a> назначен для доставки {order_info.volume} '
                                          f'литров топлива на адрес {order_info.volume}',
                                     reply_markup=kb.keyboard_confirm_select_executor())


@router.callback_query(F.data.startswith('appoint_'))
@error_handler
async def process_confirm_appoint(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение назначения водителя
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_not_del_personal_list: {callback.message.chat.id}')
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
        keyboard = kb.keyboards_executor_personal(list_users=list_users,
                                                  back=0,
                                                  forward=2,
                                                  count=6,
                                                  order_id=order_id)
        await callback.message.edit_text(text=f'Выберите ВОДИТЕЛЯ, для назначения на заказ № {order_id}',
                                         reply_markup=keyboard)
    else:
        data = await state.get_data()
        order_id = data["order_id"]
        tg_id_executor = data['tg_id_executor']
        user_info = await rq.get_user_by_id(tg_id=tg_id_executor)
        order_info: Order = await rq.get_order_id(order_id=order_id)
        await callback.message.edit_text(text=f'Заказ № {order_id} создан.\n\n'
                                              f'Плательщик: <i>{order_info.payer}</i>\n'
                                              f'Адрес: <i>{order_info.address}</i>\n'
                                              f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                              f'Время доставки: <i>{order_info.time}</i>\n'
                                              f'Количество топлива: <i>{order_info.volume} литров</i>\n'
                                              f'Водитель <a href="tg://user?id={user_info.tg_id}">'
                                              f'{user_info.username}</a>')
        await bot.send_message(chat_id=order_info.tg_id,
                               text=f'Заказ № {order_id} создан.\n\n'
                                    f'Плательщик: <i>{order_info.payer}</i>\n'
                                    f'Адрес: <i>{order_info.address}</i>\n'
                                    f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                    f'Время доставки: <i>{order_info.time}</i>\n'
                                    f'Количество топлива: <i>{order_info.volume} литров</i>\n'  
                                    f'Водитель <a href="tg://user?id={user_info.tg_id}">'
                                    f'{user_info.username}</a>')
        await rq.set_order_executor(order_id=order_id,
                                    executor=user_info.tg_id)
        await rq.set_order_date_create(order_id=order_id,
                                       date_create=datetime.now().strftime('%d.%m.%Y %H:%M'))
        await rq.set_order_status(order_id=order_id,
                                  status=rq.OrderStatus.work)
        await bot.send_message(chat_id=tg_id_executor,
                               text=f'Заказ № {order_id}\n'
                                    f'Плательщик: <i>{order_info.payer}</i>\n'
                                    f'Адрес: <i>{order_info.address}</i>\n'
                                    f'Контактное лицо: <i>{order_info.contact}</i>\n'
                                    f'Время доставки: <i>{order_info.time}</i>\n'
                                    f'Количество топлива: <i>{order_info.volume} литров</i>\n'  
                                    f'Пришлите фото оплаченной квитанции, для этого выберите заказ в разделе "ЗАКАЗ"')
    await callback.answer()
