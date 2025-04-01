from database.models import User, Order, async_session, Token
from sqlalchemy import select, or_, and_, distinct
import logging
from dataclasses import dataclass
from datetime import datetime, date


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


async def set_user_nickname(tg_id: int, nickname: str) -> None:
    """
    Обновление никнейма пользователя
    :param tg_id:
    :param nickname:
    :return:
    """
    logging.info('set_user_phone')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.username = nickname
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


async def get_order_tg_id(tg_id: int | None) -> list[Order]:
    """
    Получаем заявки партнера
    :param tg_id:
    :return:
    """
    logging.info('get_order_tg_id')
    async with async_session() as session:
        if tg_id:
            list_orders = await session.scalars(select(Order).where(Order.tg_id == tg_id))
        else:
            list_orders = await session.scalars(select(Order))
        return [order for order in list_orders]


async def get_orders_tg_id_status(tg_id_executor: int | None, status: str) -> list[Order]:
    """
    Получаем заявки по его tg_id и заданному статусу
    :param tg_id_executor:
    :param status:
    :return:
    """
    logging.info('get_orders_tg_id_status')
    async with async_session() as session:
        if tg_id_executor:
            orders = await session.scalars(select(Order).filter(Order.executor == tg_id_executor,
                                                                Order.status == status))
        else:
            orders = await session.scalars(select(Order).where(Order.status == status))
        list_order = [order for order in orders]
        return list_order


async def get_orders_tg_id_creator_status(tg_id_creator: int | None, status: str) -> list[Order]:
    """
    Получаем заявки по его tg_id и заданному статусу
    :param tg_id_creator:
    :param status:
    :return:
    """
    logging.info('get_orders_tg_id_creator_status')
    async with async_session() as session:
        if tg_id_creator:
            orders = await session.scalars(select(Order).filter(Order.tg_id == tg_id_creator))
        else:
            orders = await session.scalars(select(Order))
        list_order = [order for order in orders]
        return list_order


async def get_orders_tg_id_creator_status_(tg_id_creator: int | None, status: str) -> list[Order]:
    """
    Получаем заявки по его tg_id и заданному статусу
    :param tg_id_creator:
    :param status:
    :return:
    """
    logging.info('get_orders_tg_id_creator_status')
    async with async_session() as session:
        if tg_id_creator:
            orders = await session.scalars(select(Order).filter(Order.tg_id == tg_id_creator,
                                                                Order.status == OrderStatus.create))
        else:
            orders = await session.scalars(select(Order).where(Order.status == OrderStatus.create))
        list_order = [order for order in orders]
        return list_order


async def get_create_orders_tg_id(tg_id_creator: int) -> list[Order]:
    """
    Получаем заявки создателя tg_id со статусом create
    :param tg_id_creator:
    :return:
    """
    logging.info('get_orders_tg_id_creator_status')
    async with async_session() as session:
        if tg_id_creator:
            orders = await session.scalars(select(Order).filter(Order.tg_id == tg_id_creator,
                                                                Order.status == OrderStatus.create))
        else:
            orders = await session.scalars(select(Order).where(Order.status == OrderStatus.create))
        list_order = [order for order in orders]
        return list_order


async def get_order_report(tg_id: int, data_1: datetime, data_2: datetime) -> (int, int):
    """
    Получаем завершенные заказы в зависимости от роли,
     для ПАРТНЕРА созданные им,
     для водителя выполненные им,
     иначе получаем все завершенные заказы.
    Производим подсчет количества заказов и отгруженного топлива
    :param tg_id:
    :param data_1:
    :param data_2:
    :return:
    """
    logging.info('get_order_report')
    async with async_session() as session:
        user = await get_user_by_id(tg_id)
        if user.role == UserRole.executor:
            orders = await session.scalars(select(Order).filter(Order.executor == tg_id,
                                                                Order.date_solution != ''))
        elif user.role == UserRole.partner:
            orders = await session.scalars(select(Order).filter(Order.tg_id == tg_id,
                                                                Order.date_solution != ''))
        else:
            orders = await session.scalars(select(Order).where(Order.date_solution != ''))
        quantity = 0
        volume = 0
        for order in orders:
            data_str = order.date_solution.split(' ')[0]
            order_data = datetime(year=int(data_str.split('-')[-1]),
                                  month=int(data_str.split('-')[-2]),
                                  day=int(data_str.split('-')[-3]))
            if data_1 <= order_data <= data_2:
                quantity += 1
                volume += float(order.volume)
        return quantity, volume


async def get_order_report_admin(data_1: datetime, data_2: datetime) -> (int, int, list[Order]):
    """
    1. Получаем все завершенные заказы в выбранный период
    2. Производим подсчет количества выполненных заказов и отгруженного топлива
    :param data_1:
    :param data_2:
    :return:
    """
    logging.info('get_order_report')
    async with async_session() as session:
        orders = await session.scalars(select(Order).filter(Order.date_solution != ''))
        quantity = 0
        volume = 0
        orders_list = []
        for order in orders:
            data_str = order.date_solution.split(' ')[0]
            order_data = datetime(year=int(data_str.split('-')[-1]),
                                  month=int(data_str.split('-')[-2]),
                                  day=int(data_str.split('-')[-3]))
            if data_1 <= order_data <= data_2:
                quantity += 1
                volume += float(order.volume)
                orders_list.append(order)
        return quantity, volume, orders_list


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


async def set_order_payer(order_id: int, payer: str) -> None:
    """
    Обновление ПЛАТЕЛЬЩИКА заявки
    :param order_id:
    :param payer:
    :return:
    """
    logging.info('set_order_payer')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.payer = payer
            await session.commit()


async def set_order_inn(order_id: int, inn: str) -> None:
    """
    Обновление ИНН заявки
    :param order_id:
    :param inn:
    :return:
    """
    logging.info('set_order_inn')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            order.inn = inn
            await session.commit()


async def set_order_report(order_id: int, photo_ids_report: str, text_order: str) -> None:
    """
    Обновление отчета в заявке
    :param order_id:
    :param photo_ids_report:
    :param text_order:
    :return:
    """
    logging.info('set_order_report')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.photo_ids_report = photo_ids_report
        order.status = OrderStatus.completed
        order.text_report = text_order
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


async def delete_order(order_id: int) -> None:
    """
    Удаление заказа
    :param order_id:
    :return:
    """
    logging.info('delete_order')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order:
            await session.delete(order)
            await session.commit()


""" TOKEN """


async def add_token(data: dict) -> None:
    """
    Добавление токена
    :param data:
    :return:
    """
    logging.info(f'add_token')
    async with async_session() as session:
        new_token = Token(**data)
        session.add(new_token)
        await session.commit()


async def get_token(token: str, tg_id: int) -> bool | str:
    """
    Проверка валидности токена
    :param token:
    :param tg_id:
    :return:
    """
    logging.info('get_token')
    async with async_session() as session:
        token_ = await session.scalar(select(Token).filter(Token.token == token,
                                                           Token.tg_id == 0))
        if token_:
            token_.tg_id = tg_id
            role = token_.role
            await session.commit()
            return role
        else:
            return False
