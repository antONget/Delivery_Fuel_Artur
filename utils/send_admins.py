from aiogram import Bot
from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup
from config_data.config import Config, load_config

config: Config = load_config()


async def send_message_admins_text(bot: Bot, text: str, keyboard: InlineKeyboardMarkup | None):
    """
    Рассылка сообщения администраторам
    :param bot:
    :param text:
    :param keyboard:
    :return:
    """
    list_admins = config.tg_bot.admin_ids.split(',')
    for admin in list_admins:
        try:
            await bot.send_message(chat_id=admin,
                                   text=text,
                                   reply_markup=keyboard)
        except:
            pass


async def send_message_admins_photo(bot: Bot, list_ids: list, caption: str):
    """
    Рассылка медиагруппы администраторам
    :param bot:
    :param list_ids:
    :param caption:
    :return:
    """
    list_admins = config.tg_bot.admin_ids.split(',')

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
            await bot.send_media_group(chat_id=admin,
                                       media=media_group)
        except:
            pass