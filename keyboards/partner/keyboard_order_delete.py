from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import User, Order


def keyboard_delete() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия с заказом
    [[Повторить],[Изменить заказ]]
    :return:
    """
    logging.info('keyboard_action_order')
    button_1 = InlineKeyboardButton(text='Удалить ',
                                    callback_data='deleteorder_confirm')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='deleteorder_cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],
                                                     [button_2],
                                                     ])
    return keyboard
