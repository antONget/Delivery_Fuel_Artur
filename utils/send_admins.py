from aiogram import Bot
from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup
from config_data.config import Config, load_config
from database.models import User
from database.requests import get_users_role, UserRole

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