import asyncio
import logging

from aiogram import Bot
from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, Message
from config_data.config import Config, load_config
from database.models import User
from database.requests import get_users_role, UserRole, add_order_receipt

config: Config = load_config()


async def send_message_admins_text(bot: Bot, text: str, keyboard: InlineKeyboardMarkup | None):
    """
    Рассылка сообщения администраторам
    :param bot:
    :param text:
    :param keyboard:
    :return:
    """
    # list_admins = config.tg_bot.admin_ids.split(',')
    list_admins: list[User] = await get_users_role(role=UserRole.admin)
    for admin in list_admins:
        try:
            await bot.send_message(chat_id=admin.tg_id,
                                   text=text,
                                   reply_markup=keyboard)
        except:
            pass


async def send_message_admins_media_group(bot: Bot, list_ids: list, caption: str):
    """
    Рассылка медиагруппы администраторам
    :param bot:
    :param list_ids:
    :param caption:
    :return:
    """
    # list_admins = config.tg_bot.admin_ids.split(',')
    list_admins: list[User] = await get_users_role(role=UserRole.admin)
    media_group = []
    i = 0
    for photo in list_ids:
        i += 1
        if i == 1:
            media_group.append(InputMediaPhoto(media=photo, caption=caption))
        else:
            media_group.append(InputMediaPhoto(media=photo))
    for admin in list_admins:
        try:
            await bot.send_media_group(chat_id=admin.tg_id,
                                       media=media_group)
        except:
            pass


async def send_message_admins_media_group_save_message(bot: Bot, list_ids: list, caption: str, order_id: int):
    """
    Рассылка медиагруппы администраторам
    :param bot:
    :param list_ids:
    :param caption:
    :return:
    """
    logging.info('send_message_admins_media_group_save_message')
    list_admins: list[User] = await get_users_role(role=UserRole.admin)
    media_group = []
    i = 0
    for photo in list_ids:
        i += 1
        if i == 1:
            media_group.append(InputMediaPhoto(media=photo, caption=caption))
        else:
            media_group.append(InputMediaPhoto(media=photo))
    for admin in list_admins:
        await asyncio.sleep(0.2)
        try:
            msg: list[Message] = await bot.send_media_group(chat_id=admin.tg_id,
                                                            media=media_group)
            await add_order_receipt(data={"order_id": order_id,
                                          "receipt_chat_id": admin.tg_id,
                                          "receipt_message_id": msg[0].message_id})
        except:
            pass