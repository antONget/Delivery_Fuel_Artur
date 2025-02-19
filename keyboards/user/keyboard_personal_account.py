from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging
from database.models import User


def keyboard_change_personal_data(info_user: User) -> InlineKeyboardMarkup:
    """
    Клавиатура для изменения персональных данных
    :param info_user:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text=f'Имя - {info_user.full_name}',
                                    callback_data=f'change_personal_data_fullname')
    button_2 = InlineKeyboardButton(text=f'Лицевой счет - {info_user.personal_account}',
                                    callback_data=f'change_personal_data_personalaccount')
    button_3 = InlineKeyboardButton(text=f'Телефон - {info_user.phone}',
                                    callback_data=f'change_personal_data_phone')
    button_4 = InlineKeyboardButton(text=f'Подтвердить',
                                    callback_data=f'change_personal_data_confirm')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4]],)
    return keyboard
