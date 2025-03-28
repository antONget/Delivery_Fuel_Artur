from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from database.models import Order
import logging


def keyboard_report_executor() -> InlineKeyboardMarkup:
    """
    Клавиатура для получения отчета админом
    :return:
    """
    logging.info('keyboard_select_mailing')
    button_1 = InlineKeyboardButton(text='Отчет за период',
                                    callback_data='report_period')
    button_2 = InlineKeyboardButton(text='Отчет за водителя',
                                    callback_data='report_executor')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_report_admin() -> InlineKeyboardMarkup:
    """
    Клавиатура для получения отчета админом
    :return:
    """
    logging.info('keyboard_select_mailing')
    button_1 = InlineKeyboardButton(text='Отчет общий',
                                    callback_data='report_general')
    button_2 = InlineKeyboardButton(text='Отчет за партнера',
                                    callback_data='report_partner')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_report_item_one(list_item: list[Order], block: int) -> InlineKeyboardMarkup:
    """
    Список отчетов
    :param list_item:
    :param block:
    :return:
    """
    logging.info(f'keyboards_report_item_one')
    count_item = len(list_item)
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'itemreport_minus_{str(block)}')
    button_count = InlineKeyboardButton(text=f'{count_item}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'itemreport_plus_{str(block)}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_back, button_count, button_next]])
    return keyboard
