from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from database.requests import UserRole
import logging


def keyboard_start(role: str) -> ReplyKeyboardMarkup:
    """
    Стартовая клавиатура для каждой роли
    :param role:
    :return:
    """
    logging.info("keyboard_start")
    keyboard = ''
    if role == UserRole.admin:
        button_1 = KeyboardButton(text='Персонал')
        button_2 = KeyboardButton(text='Заказы')
        button_3 = KeyboardButton(text='Отчет')
        button_4 = KeyboardButton(text='Необработанные заявки')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3], [button_4]],
                                       resize_keyboard=True)
    elif role == UserRole.partner:
        button_1 = KeyboardButton(text='Заказы')
        button_2 = KeyboardButton(text='Отчет')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                       resize_keyboard=True)
    elif role == UserRole.executor:
        button_1 = KeyboardButton(text='Отчет')
        button_2 = KeyboardButton(text='Заказ')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                       resize_keyboard=True)
    return keyboard


def keyboard_change_role_admin() -> InlineKeyboardMarkup:
    logging.info("keyboard_change_role_admin")
    button_1 = InlineKeyboardButton(text='Изменить', callback_data=f'change_role_admin')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_select_role_admin() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_role_admin")
    button_1 = InlineKeyboardButton(text='Администратор', callback_data=f'select_role_admin')
    button_2 = InlineKeyboardButton(text='Водитель', callback_data=f'select_role_executor')
    button_3 = InlineKeyboardButton(text='Партнер', callback_data=f'select_role_partner')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])
    return keyboard
