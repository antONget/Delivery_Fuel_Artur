from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Order
import logging


def keyboard_report() -> InlineKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='В работе',
                                    callback_data='order_work')
    button_2 = InlineKeyboardButton(text='Завершенные',
                                    callback_data='order_completed')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_select_item_one(list_item: list[Order], block: int, type_order: str) -> InlineKeyboardMarkup:
    """
    Список заявок выводится по одной
    :param list_item:
    :param block:
    :param type_order:
    :return:
    """
    logging.info(f'keyboards_select_item_one')
    count_item = len(list_item)
    if block == count_item:
        block = 0
    elif block < 0:
        block = count_item - 1
    button_select = InlineKeyboardButton(text='Выбрать',
                                         callback_data=f'itemselect_select_{str(list_item[block].id)}')
    button_cancel = InlineKeyboardButton(text='Отказаться',
                                         callback_data=f'itemselect_cancel_{str(list_item[block].id)}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'itemselect_minus_{str(block)}')
    button_count = InlineKeyboardButton(text=f'{count_item}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'itemselect_plus_{str(block)}')
    if type_order == 'completed':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_back, button_count, button_next]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_select, button_cancel],
                                                         [button_back, button_count, button_next]])
    return keyboard


def keyboard_send_report() -> InlineKeyboardMarkup:
    """
    Клавиатура для добавления материалов к отчету
    :return:
    """
    logging.info("keyboard_send_report")
    button_1 = InlineKeyboardButton(text=f'Отправить отчет',
                                    callback_data=f'send_report_continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_pass_comment(order_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для пропуска отправки комментария при отказе от выполнения заказа
    :return:
    """
    logging.info("keyboard_pass_comment")
    button_1 = InlineKeyboardButton(text=f'Пропустить',
                                    callback_data=f'pass_comment')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard



