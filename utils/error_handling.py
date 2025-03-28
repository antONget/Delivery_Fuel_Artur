import traceback
from aiogram.types import Message, CallbackQuery
import logging as logs
from functools import wraps
from aiogram import Bot
from config_data.config import Config, load_config

config: Config = load_config()


def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            func_name = func.__name__
            func_doc = func.__doc__

            # Получаем полную информацию об ошибке (включая стек вызовов и номер строки)
            error_traceback = traceback.format_exc()

            # Получаем объект сообщения
            message = next(
                (arg for arg in args if isinstance(arg, Message)), None)
            bot = kwargs.get('bot')
            
            if not message:
                callback = next(
                    (arg for arg in args if isinstance(arg, CallbackQuery)), None)
                if callback:
                    message = callback.message

            if message:
                await message.answer(text='Упс.. Что-то пошло не так( Перезапустите бота /start')

            
            # Лог ошибки
            # logs.error(f"Ошибка у пользователя {message.from_user.id if message else ''}.\nОшибка в функции {func_name} ({func_doc}):\n{str(e)}\n{error_traceback}")
            if len(error_traceback) > 4000:
                for error_ in error_traceback[::4000]:
                    await bot.send_message(chat_id=config.tg_bot.support_id,
                                           text=f"Ошибка у пользователя {message.from_user.id if message else ''}.\n"
                                                f"Ошибка в функции {func_name} ({func_doc}):\n"
                                                f"{str(e)}\n"
                                                f"{error_}")
            else:
                await bot.send_message(chat_id=config.tg_bot.support_id,
                                       text=f"Ошибка у пользователя {message.from_user.id if message else ''}.\n"
                                            f"Ошибка в функции {func_name} ({func_doc}):\n"
                                            f"{str(e)}\n"
                                            f"{error_traceback}")
    return wrapper