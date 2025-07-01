import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile
from database.requests import set_order_status
from config_data.config import Config, load_config
import logging

router = Router()
config: Config = load_config()


@router.callback_query()
async def all_callback(callback: CallbackQuery) -> None:
    logging.info(f'all_callback:{callback.data} {callback.from_user.id}')
    logging.info(callback.data)


@router.message(F.text.startswith('/ordertocreate'))
async def order(message: Message) -> None:
    logging.info(f'order {message.text}')
    list_admin = config.tg_bot.admin_ids.split(',')
    if str(message.from_user.id) in list_admin:
        if len(message.text.split(' ')) == 2:
            order_id = message.text.split(' ', maxsplit=1)[-1]
            if order_id.isdigit():
                order_id = int(order_id)
                await set_order_status(order_id=order_id, status='create')
                await message.answer(text=f'Заказу № {order_id} присвоен статус CREATE')
            else:
                await message.answer(text='Номер заказа должен быть числом')
        else:
            await message.answer(text='Для применения команды необходимо через пробел указать номер заказа,'
                                      ' например:/ordertocreate 100')
    else:
        await message.answer(text='Вам не доступна эта команда')


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message {message.text} {message.from_user.id}')
    if message.video:
        logging.info(f'all_message message.photo')
        logging.info(message.video.file_id)
    if message.photo:
        logging.info(f'all_message message.photo')
        logging.info(message.photo[-1].file_id)

    if message.sticker:
        logging.info(f'all_message message.sticker')
        logging.info(message.sticker.file_id)

    if message.text == '/get_logfile':
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))

    if message.text == '/get_DB':
        file_path = "database/db.sqlite3"
        await message.answer_document(FSInputFile(file_path))
    # else:
    #     msg = await message.answer(text='')
    #     await message.delete()
    #     await asyncio.sleep(5)
    #     await msg.delete()

