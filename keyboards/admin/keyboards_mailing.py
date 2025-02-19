from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_mailing() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа рассылки
    :return:
    """
    logging.info('keyboard_select_mailing')
    button_1 = InlineKeyboardButton(text='Опрос',
                                    callback_data='survey')
    button_2 = InlineKeyboardButton(text='Оповещение',
                                    callback_data='notification')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_send_servey() -> InlineKeyboardMarkup:
    """
    Клавиатура для отправки опроса
    :return:
    """
    logging.info('keyboard_send_servey')
    button_1 = InlineKeyboardButton(text='Отправить',
                                    callback_data='send_survey')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_send_notification() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора отправки
    :return:
    """
    logging.info('keyboard_send_notification')
    button_1 = InlineKeyboardButton(text='ДА',
                                    callback_data='notification_yes')
    button_2 = InlineKeyboardButton(text='НЕТ',
                                    callback_data='notification_no')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
    return keyboard
