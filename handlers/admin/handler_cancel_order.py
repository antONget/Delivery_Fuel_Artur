from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from utils.error_handling import error_handler
from config_data.config import Config, load_config
from database.models import Order, OrderAdminEdit, OrderPartnerDelete, User
from database import requests as rq
from keyboards.partner.keyboard_order import keyboard_delete_partner

import logging


router = Router()
config: Config = load_config()


class CancelOrder(StatesGroup):
    reason = State()


# Персонал

@router.callback_query(F.data.startswith('returnorder_'))
@error_handler
async def process_cancel_order(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Отмена полученного заказа
    :param callback: returnorder_{order_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_cancel_order: {callback.from_user.id}')
    order_id = int(callback.data.split('_')[-1])
    await state.update_data(order_id=order_id)
    await callback.message.edit_text(text=f'Пришлите причину отмены заказа')
    await state.set_state(CancelOrder.reason)
    await callback.answer()


@router.message(F.text, StateFilter(CancelOrder.reason))
async def get_reason_cancel_order(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем никнейм для обновления
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_reason_cancel_order')
    reason = message.text
    data = await state.get_data()
    info_order: Order = await rq.get_order_id(order_id=data.get('order_id'))
    await message.answer(text=f'Заказ №{info_order.id} отменен')
    messages_order: list[OrderAdminEdit] = await rq.get_order_admin_edit(order_id=info_order.id)
    for info_message in messages_order:
        try:
            await bot.delete_message(chat_id=info_message.chat_id,
                                     message_id=info_message.message_id)
        except:
            pass
    await rq.delete_order_admin_edit(order_id=info_order.id)
    try:
        message_partner: OrderPartnerDelete = await rq.get_order_partner_delete(order_id=info_order.id)
        await bot.delete_message(chat_id=message_partner.partner_tg_id,
                                 message_id=message_partner.message_id,)
        msg_partner = await bot.send_message(chat_id=message_partner.partner_tg_id,
                                             text=f'Ваш заказ №{info_order.id} отменен по причине:\n{reason}',
                                             reply_markup=keyboard_delete_partner(order_id=info_order.id))
        await rq.update_order_partner_delete(order_id=info_order.id, message_id=msg_partner.message_id)
    except:
        await message.answer(text='Бот не смог оповестить заказчика об отмене заказа')
    list_admins: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
    for admin in list_admins:
        try:
            await bot.send_message(chat_id=admin.tg_id,
                                   text=f'Заказ №{info_order.id} был удален администратором '
                                        f'<a href="tg://user?id={message.from_user.id}">'
                                        f'{message.from_user.username}</a>',
                                   reply_markup=None)
        except:
            pass
    await state.set_state(state=None)
