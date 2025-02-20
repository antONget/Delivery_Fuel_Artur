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
    address: Mapped[str] = mapped_column(String)
    volume: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    date_create: Mapped[str] = mapped_column(String)
    executor: Mapped[int] = mapped_column(BigInteger, default=0)
    date_solution: Mapped[str] = mapped_column(String, default='')
    text_report: Mapped[str] = mapped_column(String, default='')
    photo_ids_report: Mapped[str] = mapped_column(String, default='')


class Token(Base):
    __tablename__ = 'token'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    tg_id: Mapped[int] = mapped_column(BigInteger, default=0)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


