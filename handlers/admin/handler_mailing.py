from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter

import keyboards.admin.keyboards_mailing as kb
import database.requests as rq
from database.models import User
from filter.admin_filter import IsSuperAdmin
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins_text


import asyncio
import logging


router = Router()


class Mailing(StatesGroup):
    survey = State()
    option = State()
    notification = State()


# Персонал
@router.message(F.text == 'Рассылка', IsSuperAdmin())
@error_handler
async def process_mailing(message: Message, bot: Bot) -> None:
    """
    Запуск процесса рассылки
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'process_mailing: {message.chat.id}')
    await message.answer(text="Выберите что бы вы хотели отправить пользователям",
                         reply_markup=kb.keyboard_select_mailing())


@router.callback_query(F.data == 'survey')
@error_handler
async def servey_process(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Формирование опроса
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('survey_process')
    await callback.message.edit_text(text='Пришлите вопрос для проведения опроса',
                                     reply_markup=None)
    await state.set_state(Mailing.survey)
    await callback.answer()


@router.message(StateFilter(Mailing.survey))
@error_handler
async def get_question_servey(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем вопрос для проведения опроса
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_question_servey')
    question_survey = message.text
    await state.update_data(question_survey=question_survey)
    await message.answer(text='Пришлите вариант ответа')
    await state.update_data(list_option=[])
    await state.set_state(Mailing.option)


@router.message(StateFilter(Mailing.option), F.text)
@error_handler
async def poll(message: Message, state: FSMContext, bot: Bot):
    """
    Отправка опроса
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('poll')
    data = await state.get_data()
    list_option: list = data['list_option']
    list_option.append(message.text)
    if len(list_option) > 1:
        await state.update_data(options=list_option)
        await message.answer_poll(question=data['question_survey'],
                                  options=list_option,
                                  type='quiz',
                                  correct_option_id=1,
                                  is_anonymous=False)
        await message.answer(text='Вы можете добавить вариант ответа или отправить опрос в рассылку',
                             reply_markup=kb.keyboard_send_servey())
    else:
        await message.answer(text='Добавьте вариант ответа')


@router.callback_query(F.data == 'send_survey')
@error_handler
async def send_survey(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Отправка опроса
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    await state.set_state(state=None)
    users_list: list[User] = await rq.get_users_role(role=rq.UserRole.user)
    data: dict = await state.get_data()
    question: str = data['question_survey']
    options: list = data['options']
    await callback.message.answer(text=f'Рассылка опроса запущена на {len(users_list)} пользователей')
    count: int = 0
    for user in users_list:
        try:
            await bot.send_poll(chat_id=user.tg_id,
                                question=question,
                                options=options,
                                type='quiz',
                                correct_option_id=1,
                                is_anonymous=False)
            count += 1
        except:
            pass
    await callback.message.answer(text=f'Опрос успешно разослан до {count}/{len(users_list)} пользователей')


@router.poll_answer()
@error_handler
async def poll_answer(poll_answer: PollAnswer, bot: Bot):
    """
    Получаем результаты опроса
    :param poll_answer:
    :return:
    """
    logging.info('poll_answer')
    answer_ids = poll_answer.option_ids  # list of answers
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id
    await send_message_admins_text(bot=bot,
                                   text=f'answer_ids: {answer_ids}, user_id: {user_id}, poll_id: {poll_id}',
                                   keyboard=None)


@router.callback_query(F.data == 'notification')
@error_handler
async def notification_process(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Формирование опроса
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('notification_process')
    await callback.message.edit_text(text='Пришлите текст для оповещения пользователей',
                                     reply_markup=None)
    await state.set_state(Mailing.notification)
    await callback.answer()


@router.message(StateFilter(Mailing.notification), F.text)
@error_handler
async def notification(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем сообщение для оповещения
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('notification')
    notification_text = message.text
    await state.update_data(notification_text=notification_text)
    await message.answer(text=f'Отправить оповещение\n\n'
                              f'{notification_text}',
                         reply_markup=kb.keyboard_send_notification())


@router.callback_query(F.data.startswith('notification_'))
@error_handler
async def send_notification(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Отправка
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('send_notification')
    answer = callback.data.split('_')[-1]
    data = await state.get_data()
    if answer == 'yes':
        users: list[User] = await rq.get_users_role(role=rq.UserRole.user)
        await callback.message.edit_text(text=f'Запущена рассылка оповещения на {len(users)} пользователей',
                                         reply_markup=None)
        count = 0
        for user in users:
            try:
                await bot.send_message(chat_id=user.tg_id,
                                       text=data['notification_text'])
                count += 1
            except:
                pass
        await callback.message.answer(text=f'Рассылка оповещения завершена.'
                                           f' Оповещено {count}/{len(users)} пользователей')
    elif answer == 'no':
        await callback.message.edit_text(text='Отправка оповещения отменено',
                                         reply_markup=None)
    await state.set_state(state=None)
    await callback.answer()
