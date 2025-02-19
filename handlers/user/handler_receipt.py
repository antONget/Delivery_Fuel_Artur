from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

import keyboards.user.keyboard_order as kb
from keyboards.start_keyboard import keyboard_start
import database.requests as rq
from database.models import User
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_photo, send_message_admins_text
from config_data.config import Config, load_config
from utils.search_account import search_receipt

import logging
from datetime import datetime, timedelta

config: Config = load_config()
router = Router()


class ReceiptState(StatesGroup):
    receipt = State()



@router.message(F.text == 'Квитанция')
@error_handler
async def press_button_receipt(message: Message, bot: Bot) -> None:
    """
    Запуск процедуры
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_receipt: {message.chat.id}')
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    answer: bool = await search_receipt(receipt=info_user.personal_account, personal_account=info_user.personal_account)
    if answer:
        await message.answer_document(document=FSInputFile(f'receipt/{info_user.personal_account}.pdf'))
    else:
        await message.answer(text=f'Квитанция для лицевого счета {info_user.personal_account} не найдена')
    # await message.answer(text=f'Пришлите номер вашего лицевого, например <code>7811722454330</code>')


@router.message(F.text, StateFilter(ReceiptState.receipt))
@error_handler
async def get_receipt(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем номер лицевого счета пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_receipt: {message.chat.id}')
    receipt_user = message.text
    if receipt_user.isdigit():
        await search_receipt(receipt=receipt_user, tg_id=message.from_user.id)
        await bot.send_document(chat_id=config.tg_bot.support_id,
                                document=FSInputFile(f'utils/{message.from_user.id}_subset.pdf'))
    else:
        await message.answer(text='Лицевой счет введен некорректно')


