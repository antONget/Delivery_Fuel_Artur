from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import UserRole
from database.models import User
from filter.admin_filter import check_super_admin
import logging


def keyboards_show_report(list_users: list[User], back, forward, count) -> InlineKeyboardMarkup:
    """
    Список пользователей для смены никнейма
    :param list_users:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info(f'keyboards_edit_nickname')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward >= max_forward:
        forward = max_forward
        back = forward - 2
    # print(back, forward, max_forward)
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for user in list_users[back*count:(forward-1)*count]:
        text = user.username
        button = f'personal_report_{user.tg_id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'personal_report_back_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'personal_report_forward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


def keyboard_cancel_nickname() -> InlineKeyboardMarkup:
    """
    Клавиатура для разжалования пользователя из списка персонала
    :return:
    """
    logging.info('keyboard_cancel_nickname')
    button_1 = InlineKeyboardButton(text='Отменить',
                                    callback_data='not_change_nickname')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboards_executor_personal(list_users: list[User], back: int,
                                forward: int, count: int, order_id: int) -> InlineKeyboardMarkup:
    """
    Список водителей для назначения на заказ
    :param list_users:
    :param back:
    :param forward:
    :param count:
    :param order_id:
    :return:
    """
    logging.info(f'keyboards_executor_personal')
    # print(back, forward)
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_users)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward >= max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for user in list_users[back*count:(forward-1)*count]:
        text = user.username
        button = f'executor_select_{order_id}_{user.tg_id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'executor_select_back_{order_id}_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'executor_select_forward_{order_id}_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()