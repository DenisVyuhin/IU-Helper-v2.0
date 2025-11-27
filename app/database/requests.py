from app.database.models import User, Bot, Post
from app.database.models import async_session
from sqlalchemy import select, delete, func

import constants as con


#! Операции с ползователем
async def add_user(tg_id, name):
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.tg_id == tg_id))

      if not user:
         session.add(User(tg_id=tg_id, name=name, stars=0, posts=0))
         await session.commit()


async def get_user(tg_id: int):
   async with async_session() as session:
      return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_by_id(id: int):
   async with async_session() as session:
      return await session.scalar(select(User).where(User.id == id))


async def add_stars_for_post(tg_id: int):
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.tg_id == tg_id))

      if user:
         user.posts += 1
         user.stars += con.post_price
         await session.commit()
         return True
      else:
         return False


async def add_stars(tg_id: int, amount: int):
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.tg_id == tg_id))

      if user:
         user.stars += amount
         await session.commit()
         return True
      else:
         return False


async def clear_stars(tg_id: int):
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.tg_id == tg_id))

      if user:
         user.stars = 0
         await session.commit()
         return True
      else:
         return False


async def get_users_count():
   async with async_session() as session:
      result = await session.scalar(select(func.count()).select_from(User))
      return result


#! Операции с ботом
async def add_bot_stats(tg_id: int):
   async with async_session() as session:
      bot = await session.scalar(select(Bot).where(Bot.tg_id == tg_id))

      if not bot:
         session.add(Bot(tg_id=tg_id, find_posts=0, published_posts=0, debit_stars=0))
         await session.commit()


# Объект бота
async def get_bot_info(tg_id: int):
   async with async_session() as session:
      return await session.scalar(select(Bot).where(Bot.tg_id == tg_id))


# Увеличиваем кол-во найденых ДЗ
async def add_find_posts(tg_id: int):
   async with async_session() as session:
      bot = await session.scalar(select(Bot).where(Bot.tg_id == tg_id))

      if bot:
         bot.find_posts += 1
         await session.commit()
         return True
      else:
         return False


# Увеличиваем кол-во выложенных ДЗ
async def add_published_posts(tg_id: int):
   async with async_session() as session:
      bot = await session.scalar(select(Bot).where(Bot.tg_id == tg_id))

      if bot:
         bot.published_posts += 1
         await session.commit()
         return True
      else:
         return False


# Увеличиваем сумму выведенных ДЗ
async def add_debit_stars(tg_id: int, amount: int):
   async with async_session() as session:
      bot = await session.scalar(select(Bot).where(Bot.tg_id == tg_id))

      if bot:
         bot.debit_stars += amount
         await session.commit()
         return True
      else:
         return False


#! Операции с постами
async def add_post(post_id, key, tags, url):
   async with async_session() as session:
      post = await session.scalar(select(Post).where(Post.key == key))

      if not post and tags:
         session.add(Post(post_id=post_id, key=key, tag=tags, url=url))
         await session.commit()


async def get_post_url(tag: str):
   async with async_session() as session:
      return await session.scalar(select(Post).where(Post.tag == tag))


async def get_posts_url(tag: str):
   async with async_session() as session:
      results = await session.execute(select(Post).where(Post.tag == tag))
      return results.scalars().all()


async def remove_post(key: str):
   async with async_session() as session:
      post = await session.scalar(select(Post).where(Post.key == key))

      if post:
         await session.delete(post)
         await session.commit()
         return True
      else:
         return False


async def remove_all_posts():
   async with async_session() as session:
      await session.execute(delete(Post))
      await session.commit()