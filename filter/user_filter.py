from aiogram.filters import BaseFilter
from aiogram.types import Message
from database import requests as rq
import logging


async def check_role(tg_id: int, role: str) -> bool:
    """
    Проверка на роль пользователя
    :param tg_id: id пользователя телеграм
    :param role: str
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('check_role')
    user = await rq.get_user_by_id(tg_id=tg_id)
    return user.role == role


class IsRoleAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await check_role(tg_id=message.chat.id, role=rq.UserRole.admin)


class IsRoleExecutor(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await check_role(tg_id=message.chat.id, role=rq.UserRole.executor)

