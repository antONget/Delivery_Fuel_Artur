from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging


def keyboard_quality_answer(order_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки качества ответа
    :return:
    """
    logging.info("keyboard_partner_reject")
    button_1 = InlineKeyboardButton(text='⭐⭐⭐⭐⭐', callback_data=f'quality_5_{order_id}')
    button_2 = InlineKeyboardButton(text='⭐⭐⭐⭐', callback_data=f'quality_4_{order_id}')
    button_3 = InlineKeyboardButton(text='⭐⭐⭐', callback_data=f'quality_3_{order_id}')
    button_4 = InlineKeyboardButton(text='⭐⭐', callback_data=f'quality_2_{order_id}')
    button_5 = InlineKeyboardButton(text='⭐', callback_data=f'quality_1_{order_id}')
    button_6 = InlineKeyboardButton(text='Заявка не выполнена', callback_data=f'quality_0_{order_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2],
                                                     [button_3], [button_4],
                                                     [button_5], [button_6]],)
    return keyboard


def keyboard_pass_comment() -> InlineKeyboardMarkup:
    """
    Клавиатура для пропуска добавления комментария
    :return:
    """
    logging.info("keyboard_pass_comment")
    button_1 = InlineKeyboardButton(text='Пропустить', callback_data=f'pass_comment')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard