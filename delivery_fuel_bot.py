from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data.config import Config, load_config
from handlers import error, other_handlers, start_handler
from handlers.partner import handler_report, handler_order, handler_order_repiet, handler_order_delete, \
    handler_order_change, handler_create_order, handler_order_edition
from handlers.user import handler_select_order
from handlers.admin import handler_edit_list_personal, handler_edit_nickname, handler_show_create_order, \
    handler_report_executor, handler_appointment_performer_order, handler_cancel_order
from notify_admins import on_startup_notify
from database.models import async_main

import asyncio
import logging

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    """
    Основной файл для запуска
    :return:
    """
    await async_main()
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await on_startup_notify(bot=bot)
    # Регистрируем router в диспетчере
    dp.include_router(error.router)
    dp.include_router(start_handler.router)
    dp.include_routers(handler_edit_list_personal.router,
                       handler_edit_nickname.router,
                       handler_report_executor.router,
                       handler_appointment_performer_order.router,
                       handler_create_order.router)
    dp.include_router(handler_select_order.router)
    dp.include_routers(handler_order.router,
                       handler_report.router,
                       handler_order_repiet.router,
                       handler_order_delete.router,
                       handler_show_create_order.router,
                       handler_order_edition.router,
                       handler_order_change.router,
                       handler_cancel_order.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
