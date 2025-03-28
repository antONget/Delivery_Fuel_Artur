from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import User, Order


def keyboard_action_order() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия с заказом
    :return:
    """
    logging.info('keyboard_action_order')
    button_1 = InlineKeyboardButton(text='Создать',
                                    callback_data='new_order')
    button_2 = InlineKeyboardButton(text='Повторить',
                                    callback_data='repeat_order')
    button_3 = InlineKeyboardButton(text='Удалить',
                                    callback_data='delete_order')
    button_4 = InlineKeyboardButton(text='Редактировать',
                                    callback_data='edit_order')
    button_5 = InlineKeyboardButton(text='Изменить реквизиты заказа',
                                    callback_data='change_order')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2], [button_3, button_4], [button_5]])
    return keyboard


def keyboards_executor_personal(list_users: list[User], back: int,
                                forward: int, count: int, order_id: int) -> InlineKeyboardMarkup:
    """
    Список водителей для назначения на заказ
    :param list_users:
    :param back:
    :param forward:
    :param count:
    :param order_id:
    :return:
    """
    logging.info(f'keyboards_executor_personal')
    print(back, forward)
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward >= max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for user in list_users[back*count:(forward-1)*count]:
        text = user.username
        button = f'executor_select_{order_id}_{user.tg_id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'executor_select_back_{order_id}_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'executor_select_forward_{order_id}_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


def keyboard_confirm_select_executor() -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения выбора водителя
    :return:
    """
    logging.info('keyboard_select_mailing')
    button_1 = InlineKeyboardButton(text='Подтвердить',
                                    callback_data='appoint_confirm')
    button_2 = InlineKeyboardButton(text='Отменить',
                                    callback_data='appoint_cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_payer(list_orders: list[Order], block: int = 0) -> InlineKeyboardMarkup:
    """
    Список плательщиков
    :param list_orders:
    :param block:
    :return:
    """
    logging.info(f'keyboards_payer')
    button_select = InlineKeyboardButton(text='Выбрать',
                                         callback_data=f'select_payer_{list_orders[block].id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'payerlist_back_{block}')
    button_count = InlineKeyboardButton(text=f'{block+1}/{len(list_orders)}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'payerlist_next_{block}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_select],
                                                     [button_back, button_count, button_next]])

    return keyboard


def keyboards_inn(list_orders: list[Order], block: int = 0) -> InlineKeyboardMarkup:
    """
    Список плательщиков
    :param list_orders:
    :param block:
    :return:
    """
    logging.info(f'keyboards_payer')
    button_select = InlineKeyboardButton(text='Выбрать',
                                         callback_data=f'select_inn_{list_orders[block].id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'innlist_back_{block}')
    button_count = InlineKeyboardButton(text=f'{block+1}/{len(list_orders)}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'innlist_next_{block}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_select],
                                                     [button_back, button_count, button_next]])

    return keyboard


def keyboards_contact(list_orders: list[Order], block: int = 0) -> InlineKeyboardMarkup:
    """
    Список контактов
    :param list_orders:
    :param block:
    :return:
    """
    logging.info(f'keyboards_payer')
    button_select = InlineKeyboardButton(text='Выбрать',
                                         callback_data=f'select_contact_{list_orders[block].id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'contactlist_back_{block}')
    button_count = InlineKeyboardButton(text=f'{block+1}/{len(list_orders)}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'contactlist_next_{block}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_select],
                                                     [button_back, button_count, button_next]])

    return keyboard


def keyboard_time_interval() -> InlineKeyboardMarkup:
    """
    Список временных интервалов доставки
    :return:
    """
    logging.info(f'keyboards_payer')
    button_1 = InlineKeyboardButton(text='8.00-11.00',
                                    callback_data=f'timeinterval_8.00-11.00')
    button_2 = InlineKeyboardButton(text='11.00-14.00',
                                    callback_data=f'timeinterval_11.00-14.00')
    button_3 = InlineKeyboardButton(text='14.00-17.00',
                                    callback_data=f'timeinterval_14.00-17.00')
    button_4 = InlineKeyboardButton(text='17.00-19.00',
                                    callback_data=f'timeinterval_17.00-19.00')
    button_5 = InlineKeyboardButton(text='Другое',
                                    callback_data=f'timeinterval_other')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2], [button_3, button_4], [button_5]])

    return keyboard
