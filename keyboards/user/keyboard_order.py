from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging
from database.models import User


def keyboard_type_report() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа заявки
    :return:
    """
    logging.info("keyboard_type_report")
    button_1 = InlineKeyboardButton(text=f'Частные',
                                    callback_data=f'type_order_private')
    button_2 = InlineKeyboardButton(text=f'Общедомовые',
                                    callback_data=f'type_order_general')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_send_order() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа заявки
    :return:
    """
    logging.info("keyboard_type_report")
    button_1 = InlineKeyboardButton(text=f'Добавить фото',
                                    callback_data=f'send_order_photo')
    button_2 = InlineKeyboardButton(text=f'Далее',
                                    callback_data=f'send_order_continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_assign_performer(order_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для назначения исполнителя
    :return:
    """
    logging.info("keyboard_assign_performer")
    button_1 = InlineKeyboardButton(text=f'Назначить исполнителя',
                                    callback_data=f'assign_performer_{order_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard
