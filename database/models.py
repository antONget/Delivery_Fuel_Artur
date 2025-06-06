from sqlalchemy import String, Integer, DateTime, BigInteger, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:///database/db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, default='user')


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    payer: Mapped[str] = mapped_column(String)
    inn: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    contact: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String)
    time: Mapped[str] = mapped_column(String)
    volume: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    date_create: Mapped[str] = mapped_column(String)
    executor: Mapped[int] = mapped_column(BigInteger, default=0)
    date_solution: Mapped[str] = mapped_column(String, nullable=True)
    text_report: Mapped[str] = mapped_column(String, nullable=True)
    photo_ids_report: Mapped[str] = mapped_column(String, nullable=True)


class Token(Base):
    __tablename__ = 'token'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    tg_id: Mapped[int] = mapped_column(BigInteger, default=0)


class OrderReceipt(Base):
    __tablename__ = 'order_reports'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer)
    receipt_chat_id: Mapped[int] = mapped_column(Integer)
    receipt_message_id: Mapped[int] = mapped_column(Integer)


class OrderPartnerDelete(Base):
    __tablename__ = 'order_partner_delete'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer)
    partner_tg_id: Mapped[int] = mapped_column(Integer)
    message_id: Mapped[int] = mapped_column(Integer)


class OrderAdminEdit(Base):
    __tablename__ = 'order_admin_edit'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer)
    chat_id: Mapped[int] = mapped_column(Integer)
    message_id: Mapped[int] = mapped_column(Integer)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


