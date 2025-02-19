from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User
import logging


def keyboard_select_role() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора роли для редактирования
    :return:
    """
    logging.info('keyboard_select_role')
    button_1 = InlineKeyboardButton(text='Партнер',
                                    callback_data='edit_list_partner')
    button_2 = InlineKeyboardButton(text='Водитель',
                                    callback_data='edit_list_executor')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_select_action() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия которое нужно совершить с ролью
    :return:
    """
    logging.info('keyboard_select_action')
    button_1 = InlineKeyboardButton(text='Назначить',
                                    callback_data='personal_add')
    button_2 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='personal_delete')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
    return keyboard


# def keyboards_add_partner(list_admin, back, forward, count) -> InlineKeyboardMarkup:
#     """
#     Клавиатура с пагинацией для добавления персонала
#     :param list_admin:
#     :param back:
#     :param forward:
#     :param count:
#     :return:
#     """
#     logging.info(f'keyboards_add_partner')
#     # проверка чтобы не ушли в минус
#     if back < 0:
#         back = 0
#         forward = 2
#     # считаем сколько всего блоков по заданному количество элементов в блоке
#     count_users = len(list_admin)
#     whole = count_users // count
#     remains = count_users % count
#     max_forward = whole + 1
#     # если есть остаток то, увеличиваем количество блоков на один, чтобы показать остаток
#     if remains:
#         max_forward = whole + 2
#     if forward > max_forward:
#         forward = max_forward
#         back = forward - 2
#     kb_builder = InlineKeyboardBuilder()
#     buttons = []
#     for row in list_admin[back*count:(forward-1)*count]:
#         text = row[1]
#         button = f'admin_add_{row[0]}'
#         buttons.append(InlineKeyboardButton(
#             text=text,
#             callback_data=button))
#     button_back = InlineKeyboardButton(text='<<<<',
#                                        callback_data=f'admin_back_{str(back)}')
#     button_count = InlineKeyboardButton(text=f'{back+1}',
#                                         callback_data='none')
#     button_next = InlineKeyboardButton(text='>>>>',
#                                        callback_data=f'admin_forward_{str(forward)}')
#
#     kb_builder.row(*buttons, width=1)
#     kb_builder.row(button_back, button_count, button_next)
#
#     return kb_builder.as_markup()


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


def keyboards_del_personal(list_users: list[User], back, forward, count) -> InlineKeyboardMarkup:
    """
    Список пользователей для удаления из персонала
    :param list_users:
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info(f'keyboards_del_personal')
    print(back, forward)
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
    print(back, forward, max_forward)
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for user in list_users[back*count:(forward-1)*count]:
        text = user.username
        button = f'personal_del_{user.tg_id}'
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
