from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def utils_keyboards_list_items(part_list_items: list,
                               callback_prefix_select: str,
                               callback_prefix_back: str,
                               callback_prefix_next: str,
                               page: int,
                               max_page: int,
                               pagination: bool) -> InlineKeyboardMarkup:
    """
    Клавиатура для вывода списка в виде кнопок в столбец
    :param part_list_items:
    :param callback_prefix_select:
    :param callback_prefix_back:
    :param callback_prefix_next:
    :param page:
    :param max_page:
    :param pagination:
    :return:
    """
    logging.info(f"utils_keyboards_list_items")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for item in part_list_items:
        item_button = item
        item_callback = item
        buttons.append(InlineKeyboardButton(text=item_button,
                                            callback_data=f'{callback_prefix_select}_{item_callback}'))
    kb_builder.row(*buttons, width=8)
    if pagination:
        button_back = InlineKeyboardButton(text='Назад',
                                           callback_data=f'{callback_prefix_back}_{page}')
        button_next = InlineKeyboardButton(text='Вперед',
                                           callback_data=f'{callback_prefix_next}_{page}')
        button_page = InlineKeyboardButton(text=f'{page+1}/{max_page}',
                                           callback_data=f'none')
        kb_builder.row(button_back, button_page, button_next)
    return kb_builder.as_markup()


async def utils_handler_pagination_and_select_item(list_items: list,
                                                   text_message_pagination: str,
                                                   page: int,
                                                   count_item_page: int,
                                                   callback_prefix_select: str,
                                                   callback_prefix_back: str,
                                                   callback_prefix_next: str,
                                                   callback: CallbackQuery | None,
                                                   message: Message | None) -> Message:
    logging.info(f'utils_keyboard_pagination_and_select_item')
    part = 0
    pagination = True
    if len(list_items) <= count_item_page:
        pagination = False
    if len(list_items) % count_item_page:
        part = 1
    max_page = int(len(list_items)/count_item_page) + part
    if message:
        part_list_items = list_items[page * count_item_page:(page + 1) * count_item_page]
        keyboard = utils_keyboards_list_items(part_list_items=part_list_items,
                                              callback_prefix_select=callback_prefix_select,
                                              callback_prefix_back=callback_prefix_back,
                                              callback_prefix_next=callback_prefix_next,
                                              page=page,
                                              max_page=max_page,
                                              pagination=pagination)
        msg = await message.answer(text=text_message_pagination,
                                   reply_markup=keyboard)
        return msg
    if callback.data.startswith(callback_prefix_back):
        page -= 1
        if page < 0:
            page = max_page - 1
    elif callback.data.startswith(callback_prefix_next):
        page += 1
        if page == max_page:
            page = 0
    part_list_items = list_items[page*count_item_page:(page+1)*count_item_page]
    keyboard = utils_keyboards_list_items(part_list_items=part_list_items,
                                          callback_prefix_select=callback_prefix_select,
                                          callback_prefix_back=callback_prefix_back,
                                          callback_prefix_next=callback_prefix_next,
                                          page=page,
                                          max_page=max_page,
                                          pagination=pagination)
    try:
        msg = await callback.message.answer(text=text_message_pagination,
                                            reply_markup=keyboard)
    except:
        msg = await callback.message.answer(text=f'{text_message_pagination}.',
                                            reply_markup=keyboard)
    await callback.answer()
    return msg


def utils_keyboards_one_card(callback_prefix_back: str,
                             callback_prefix_next: str,
                             page: int,
                             max_page: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для вывода списка в виде кнопок в столбец
    :param callback_prefix_back:
    :param callback_prefix_next:
    :param page:
    :param max_page:
    :return:
    """
    logging.info(f"utils_keyboards_list_items")
    kb_builder = InlineKeyboardBuilder()
    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data=f'{callback_prefix_back}_{page}')
    button_next = InlineKeyboardButton(text='Вперед',
                                       callback_data=f'{callback_prefix_next}_{page}')
    button_page = InlineKeyboardButton(text=f'{page+1}/{max_page}',
                                       callback_data=f'none')
    kb_builder.row(button_back, button_page, button_next)
    return kb_builder.as_markup()


async def utils_handler_pagination_one_card_photo_or_only_text_without_select(list_items: list,
                                                                              page: int,
                                                                              callback_prefix_back: str,
                                                                              callback_prefix_next: str,
                                                                              callback: CallbackQuery | None,
                                                                              message: Message | None) -> None:
    logging.info(f'utils_handler_pagination_one_card')
    max_page = len(list_items)
    if message:
        item = list_items[page]
        keyboard = utils_keyboards_one_card(callback_prefix_back=callback_prefix_back,
                                            callback_prefix_next=callback_prefix_next,
                                            page=page,
                                            max_page=max_page)
        if item.photo:
            try:
                await message.edit_media(media=InputMediaPhoto(media=item.photo,
                                                               caption=item.description),
                                         reply_markup=keyboard)
            except:
                await message.delete()
                await message.answer_photo(photo=item.photo,
                                           caption=item.description,
                                           reply_markup=keyboard)
        else:
            try:
                await message.edit_text(text=item.description,
                                        reply_markup=keyboard)
            except:
                await message.delete()
                await message.answer(text=item.description,
                                     reply_markup=keyboard)
        return

    if callback.data.startswith(callback_prefix_back):
        page -= 1
        if page < 0:
            page = max_page - 1
    elif callback.data.startswith(callback_prefix_next):
        page += 1
        if page == max_page:
            page = 0
    item = list_items[page]
    keyboard = utils_keyboards_one_card(callback_prefix_back=callback_prefix_back,
                                        callback_prefix_next=callback_prefix_next,
                                        page=page,
                                        max_page=max_page)
    if item.photo:
        try:
            await callback.message.edit_media(media=InputMediaPhoto(media=item.photo,
                                                                    caption=item.description),
                                              reply_markup=keyboard)
        except:
            await callback.message.delete()
            await callback.message.answer_photo(photo=item.photo,
                                                caption=item.description,
                                                reply_markup=keyboard)
    else:
        try:
            await callback.message.edit_text(text=item.description,
                                             reply_markup=keyboard)
        except:
            await callback.message.delete()
            await callback.message.answer(text=item.description,
                                          reply_markup=keyboard)
    await callback.answer()


def utils_keyboards_one_card_select(text_button_select: str,
                                    item_id: int,
                                    callback_prefix_select: str,
                                    callback_prefix_back: str,
                                    callback_prefix_next: str,
                                    page: int,
                                    max_page: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для вывода кнопок пагинации и кнопки выбора
    :param text_button_select:
    :param item_id:
    :param callback_prefix_select:
    :param callback_prefix_back:
    :param callback_prefix_next:
    :param page:
    :param max_page:
    :return:
    """
    logging.info(f"utils_keyboards_list_items")
    kb_builder = InlineKeyboardBuilder()
    if text_button_select:
        button_select = InlineKeyboardButton(text=f'{text_button_select}',
                                             callback_data=f'{callback_prefix_select}_{item_id}')
        kb_builder.row(button_select)
    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data=f'{callback_prefix_back}_{page}')
    button_next = InlineKeyboardButton(text='Вперед',
                                       callback_data=f'{callback_prefix_next}_{page}')
    button_page = InlineKeyboardButton(text=f'{page+1}/{max_page}',
                                       callback_data=f'none')
    kb_builder.row(button_back, button_page, button_next)
    return kb_builder.as_markup()


async def utils_handler_pagination_one_card_photo_or_only_text(list_items: list,
                                                               page: int,
                                                               text_button_select: str,
                                                               callback_prefix_select: str,
                                                               callback_prefix_back: str,
                                                               callback_prefix_next: str,
                                                               callback: CallbackQuery | None,
                                                               message: Message | None) -> None:
    """
    Функция показывает по одной карточке из списка с фото+текст или только текст и кнопки пагинации с выбором карточки
    :param list_items:
    :param page:
    :param text_button_select:
    :param callback_prefix_select:
    :param callback_prefix_back:
    :param callback_prefix_next:
    :param callback:
    :param message:
    :return:
    """
    logging.info(f'utils_handler_pagination_one_card_photo_or_only_text')
    max_page = len(list_items)

    if message:
        item = list_items[page]
        keyboard = utils_keyboards_one_card_select(text_button_select=text_button_select,
                                                   item_id=item.id,
                                                   callback_prefix_select=callback_prefix_select,
                                                   callback_prefix_back=callback_prefix_back,
                                                   callback_prefix_next=callback_prefix_next,
                                                   page=page,
                                                   max_page=max_page)
        if item.photo:
            try:
                await message.edit_media(media=InputMediaPhoto(media=item.photo,
                                                               caption=item.short_description),
                                         reply_markup=keyboard)
            except:
                await message.delete()
                await message.answer_photo(photo=item.photo,
                                           caption=item.short_description,
                                           reply_markup=keyboard)
        else:
            try:
                await message.edit_text(text=item.short_description,
                                        reply_markup=keyboard)
            except:
                await message.delete()
                await message.answer(text=item.short_description,
                                     reply_markup=keyboard)
        return

    if callback.data.startswith(callback_prefix_back):
        page -= 1
        if page < 0:
            page = max_page - 1
    elif callback.data.startswith(callback_prefix_next):
        page += 1
        if page == max_page:
            page = 0
    item = list_items[page]
    keyboard = utils_keyboards_one_card_select(text_button_select=text_button_select,
                                               item_id=item.id,
                                               callback_prefix_select=callback_prefix_select,
                                               callback_prefix_back=callback_prefix_back,
                                               callback_prefix_next=callback_prefix_next,
                                               page=page,
                                               max_page=max_page)
    if item.photo:
        try:
            await callback.message.edit_media(media=InputMediaPhoto(media=item.photo,
                                                                    caption=item.short_description),
                                              reply_markup=keyboard)
        except:
            await callback.message.delete()
            await callback.message.answer_photo(photo=item.photo,
                                                caption=item.short_description,
                                                reply_markup=keyboard)
    else:
        try:
            await callback.message.edit_text(text=item.short_description,
                                             reply_markup=keyboard)
        except:
            await callback.message.delete()
            await callback.message.answer(text=item.short_description,
                                          reply_markup=keyboard)
    await callback.answer()


async def utils_handler_pagination_to_composite_text(list_items: list,
                                                     text_message: str,
                                                     page: int,
                                                     text_button_select: str | None,
                                                     callback_prefix_select: str,
                                                     callback_prefix_back: str,
                                                     callback_prefix_next: str,
                                                     callback: CallbackQuery | None,
                                                     message: Message | None) -> None:
    """
    Функция выводит текст переданный в параметре text_message
    :param list_items:
    :param text_message:
    :param page:
    :param text_button_select:
    :param callback_prefix_select:
    :param callback_prefix_back:
    :param callback_prefix_next:
    :param callback:
    :param message:
    :return:
    """
    logging.info(f'utils_handler_pagination_to_composite_text: page:{page}')
    max_page = len(list_items)
    if message:
        item = list_items[page]
        keyboard = utils_keyboards_one_card_select(text_button_select=text_button_select,
                                                   item_id=item.id,
                                                   callback_prefix_select=callback_prefix_select,
                                                   callback_prefix_back=callback_prefix_back,
                                                   callback_prefix_next=callback_prefix_next,
                                                   page=page,
                                                   max_page=max_page)

        try:
            await message.edit_text(text=text_message,
                                    reply_markup=keyboard)
        except:
            try:
                await message.edit_text(text=f'{text_message}.',
                                        reply_markup=keyboard)
            except:
                await message.answer(text=f'{text_message}.',
                                     reply_markup=keyboard)
        return

    item = list_items[page]
    keyboard = utils_keyboards_one_card_select(text_button_select=text_button_select,
                                               item_id=item.id,
                                               callback_prefix_select=callback_prefix_select,
                                               callback_prefix_back=callback_prefix_back,
                                               callback_prefix_next=callback_prefix_next,
                                               page=page,
                                               max_page=max_page)


    try:
        await callback.message.edit_text(text=text_message,
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'{text_message}.',
                                         reply_markup=keyboard)
    await callback.answer()
