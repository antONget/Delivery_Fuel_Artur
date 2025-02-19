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
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'itemselect_minus_{str(block)}')
    button_count = InlineKeyboardButton(text=f'{count_item}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'itemselect_plus_{str(block)}')
    if type_order == 'completed':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_back, button_count, button_next]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_select],
                                                         [button_back, button_count, button_next]])
    return keyboard


def keyboard_send_report() -> InlineKeyboardMarkup:
    """
    Клавиатура для добавления материалов к отчету
    :return:
    """
    logging.info("keyboard_send_report")
    button_1 = InlineKeyboardButton(text=f'Добавить фото',
                                    callback_data=f'send_report_photo')
    button_2 = InlineKeyboardButton(text=f'Отправить отчет',
                                    callback_data=f'send_report_continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_completed_order(order_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки выполненной заявки и просмотра отчет
    :return:
    """
    logging.info("keyboard_completed_order")
    button_1 = InlineKeyboardButton(text=f'Посмотреть отчет',
                                    callback_data=f'show_report_{order_id}')
    button_2 = InlineKeyboardButton(text=f'Оставить оценку',
                                    callback_data=f'make_quality_{order_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2]],)
    return keyboard


def keyboard_quality_answer(question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки качества ответа
    :return:
    """
    logging.info("keyboard_partner_reject")
    button_1 = InlineKeyboardButton(text='⭐⭐⭐⭐⭐', callback_data=f'quality_5_{question_id}')
    button_2 = InlineKeyboardButton(text='⭐⭐⭐⭐', callback_data=f'quality_4_{question_id}')
    button_3 = InlineKeyboardButton(text='⭐⭐⭐', callback_data=f'quality_3_{question_id}')
    button_4 = InlineKeyboardButton(text='⭐⭐', callback_data=f'quality_2_{question_id}')
    button_5 = InlineKeyboardButton(text='⭐', callback_data=f'quality_1_{question_id}')
    button_6 = InlineKeyboardButton(text='Вопрос не решен', callback_data=f'quality_0_{question_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2],
                                                     [button_3], [button_4],
                                                     [button_5], [button_6]],)
    return keyboard
