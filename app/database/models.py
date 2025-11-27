from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3") # Создаем движок
async_session = async_sessionmaker(engine)                         # Создаем сессию с движком


# Базовый класс
class Base(AsyncAttrs, DeclarativeBase):
   pass


# Класс для статистики бота
class Bot(Base):
   __tablename__ = "bot"
   id: Mapped[int] = mapped_column(primary_key=True)
   tg_id = mapped_column(BigInteger)
   find_posts: Mapped[int] = mapped_column(Integer, default=0)
   published_posts: Mapped[int] = mapped_column(Integer, default=0)
   debit_stars: Mapped[int] = mapped_column(Integer, default=0)


# Класс для пользователя
class User(Base):
   __tablename__ = "users"
   id: Mapped[int] = mapped_column(primary_key=True)
   tg_id = mapped_column(BigInteger)
   name: Mapped[str] = mapped_column(String(120))
   posts: Mapped[int] = mapped_column(Integer)
   stars: Mapped[int] = mapped_column(Integer)


# Класс для постов из ТГК (с 7 по 11 класс)
class Post(Base):
   __tablename__ = "posts"
   id: Mapped[int] = mapped_column(primary_key=True)
   post_id: Mapped[int] = mapped_column(BigInteger)
   key: Mapped[str] = mapped_column(String(120)) # Т.к. в разных тгк могут быть посты с одинковым id, то key будет содержать username + id. Так каждый пост будет иметь уникальный ключ
   tag: Mapped[str] = mapped_column(String(120))
   url: Mapped[str] = mapped_column(String(120))


# Асинхронная сессия
async def async_main():
   async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)