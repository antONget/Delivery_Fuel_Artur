from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User
import logging


def keyboards_select_executor(list_executor: list[User], back: int, forward: int, count: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с пагинацией для выбора исполнителя
    :param list_executor:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info(f'keyboards_select_executor')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_executor)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то, увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for executor in list_executor[back*count:(forward-1)*count]:
        text = executor.username
        button = f'select_executor_{executor.tg_id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'executor_back_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'executor_forward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# def keyboard_add_list_personal() -> InlineKeyboardMarkup:
#     """
#     Клавиатура для подтверждения добавления пользователя в список персонала
#     :return:
#     """
#     logging.info('keyboard_add_list_personal')
#     button_1 = InlineKeyboardButton(text='Назначить',
#                                     callback_data='add_personal_list')
#     button_2 = InlineKeyboardButton(text='Отменить',
#                                     callback_data='not_add_personal_list')
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
#     return keyboard


def keyboards_del_personal(list_admin, back, forward, count) -> InlineKeyboardMarkup:
    """
    Список пользователей для удаления из персонала
    :param list_admin:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info(f'keyboards_del_personal')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_admin)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for row in list_admin[back*count:(forward-1)*count]:
        text = row[1]
        button = f'personal_del_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'personal_del_back_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'personal_del_forward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


def keyboard_del_list_personal() -> InlineKeyboardMarkup:
    """
    Клавиатура для разжалования пользователя из списка персонала
    :return:
    """
    logging.info('keyboard_del_list_personal')
    button_1 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='del_personal_list')
    button_2 = InlineKeyboardButton(text='Отменить',
                                    callback_data='not_del_personal_list')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
    return keyboard
