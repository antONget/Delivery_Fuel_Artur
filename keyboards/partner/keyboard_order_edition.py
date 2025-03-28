from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import User, Order


def keyboard_action_repiet() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия с заказом
    :return:
    """
    logging.info('keyboard_action_order')
    button_1 = InlineKeyboardButton(text='Плательщик',
                                    callback_data='orderedit_payer')
    button_2 = InlineKeyboardButton(text='ИНН',
                                    callback_data='orderedit_inn')
    button_3 = InlineKeyboardButton(text='Адрес',
                                    callback_data='orderedit_address')
    button_4 = InlineKeyboardButton(text='Контактное лицо',
                                    callback_data='orderedit_contact')
    button_5 = InlineKeyboardButton(text='Дата доставки',
                                    callback_data='orderedit_date')
    button_6 = InlineKeyboardButton(text='Время доставки',
                                    callback_data='orderedit_time')
    button_7 = InlineKeyboardButton(text='Количество топлива',
                                    callback_data='orderedit_volume')
    button_8 = InlineKeyboardButton(text='Подтвердить',
                                    callback_data='orderedit_confirm')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],
                                                     [button_2],
                                                     [button_3],
                                                     [button_4],
                                                     [button_5],
                                                     [button_6],
                                                     [button_7],
                                                     [button_8]
                                                     ])
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
                                         callback_data=f'editselect_payer_{list_orders[block].id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'editpayerlist_back_{block}')
    button_count = InlineKeyboardButton(text=f'{block+1}/{len(list_orders)}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'editpayerlist_next_{block}')
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
                                         callback_data=f'editselect_inn_{list_orders[block].id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'editinnlist_back_{block}')
    button_count = InlineKeyboardButton(text=f'{block+1}/{len(list_orders)}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'editinnlist_next_{block}')
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
                                         callback_data=f'editselect_contact_{list_orders[block].id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'editcontactlist_back_{block}')
    button_count = InlineKeyboardButton(text=f'{block+1}/{len(list_orders)}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'editcontactlist_next_{block}')
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
                                    callback_data=f'edittimeinterval_8.00-11.00')
    button_2 = InlineKeyboardButton(text='11.00-14.00',
                                    callback_data=f'edittimeinterval_11.00-14.00')
    button_3 = InlineKeyboardButton(text='14.00-17.00',
                                    callback_data=f'edittimeinterval_14.00-17.00')
    button_4 = InlineKeyboardButton(text='17.00-19.00',
                                    callback_data=f'edittimeinterval_17.00-19.00')
    button_5 = InlineKeyboardButton(text='Другое',
                                    callback_data=f'edittimeinterval_other')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2], [button_3, button_4], [button_5]])

    return keyboard