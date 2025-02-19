from database.models import User, Order, async_session
from sqlalchemy import select, or_, and_
import logging
from dataclasses import dataclass
from datetime import datetime


""" USER """


@dataclass
class UserRole:
    user = "user"
    executor = "executor"
    admin = "admin"
    partner = "partner"


async def add_user(data: dict) -> None:
    """
    Добавление пользователя
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()
        else:
            user.username = data['username']
            await session.commit()


async def set_user_role(tg_id: int, role: str) -> None:
    """
    Обновление роли пользователя
    :param tg_id:
    :param role:
    :return:
    """
    logging.info('set_user_phone')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.role = role
            await session.commit()


async def get_user_by_id(tg_id: int) -> User:
    """
    Получение информации о пользователе по tg_id
    :param tg_id:
    :return:
    """
    logging.info(f'get_user_by_id {tg_id}')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_users_role(role: str) -> list[User]:
    """
    Получение списка пользователей с заданной ролью
    :param role:
    :return:
    """
    logging.info('get_users_role')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.role == role))
        list_users = [user for user in users]
        return list_users


""" ORDERS """


@dataclass
class OrderStatus:
    create = "create"
    work = "work"
    cancel = "cancel"
    completed = "completed"


async def add_order(data: dict) -> int:
    """
    Добавление заявки пользователя
    :param data:
    :return:
    """
    logging.info(f'add_question')
    async with async_session() as session:
        new_question = Order(**data)
        session.add(new_question)
        await session.flush()
        id_ = new_question.id
        await session.commit()
        return id_


async def get_order_id(order_id: int) -> Order:
    """
    Получаем заявку по id
    :param order_id:
    :return:
    """
    logging.info('get_order_id')
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id))


async def get_orders_tg_id_status(tg_id_executor: int, status: str) -> list[Order]:
    """
    Получаем заявки по его tg_id и заданному статусу
    :param tg_id_executor:
    :param status:
    :return:
    """
    logging.info('get_orders_tg_id_status')
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.executor == tg_id_executor,
                                                           Order.status == status))
        list_order = [order for order in orders]
        return list_order


async def set_order_status(order_id: int, status: str) -> None:
    """
    Обновление статуса заявки
    :param order_id:
    :param status:
    :return:
    """
    logging.info('set_order_status')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.status = status
            await session.commit()


async def set_order_report(order_id: int, photo_ids_report: str) -> None:
    """
    Обновление отчета в заявке
    :param order_id:
    :param photo_ids_report:
    :return:
    """
    logging.info('set_order_report')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.photo_ids_report = photo_ids_report
        order.status = OrderStatus.completed
        await session.commit()


async def set_order_executor(order_id: int, executor: int) -> None:
    """
    Добавление исполнителя к заказу
    :param order_id:
    :param executor:
    :return:
    """
    logging.info('set_order_status')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.executor = executor
            await session.commit()


async def set_order_date_solution(order_id: int, date_solution: str) -> None:
    """
    Добавление дату выполнения заявки
    :param order_id:
    :param date_solution:
    :return:
    """
    logging.info('set_order_date_solution')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.date_solution = date_solution
            await session.commit()


async def set_order_date_create(order_id: int, date_create: str) -> None:
    """
    Добавление дату создания заявки
    :param order_id:
    :param date_create:
    :return:
    """
    logging.info('set_order_date_create')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.date_create = date_create
            await session.commit()