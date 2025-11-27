import asyncio

from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Callable, Awaitable, Any, Dict

import utils.json_requests as js


# Принимаем медиа группу
class TestMiddleware(BaseMiddleware):
   def __init__(self, timeout: float = 0.2):
      self.timeout = timeout
      self.album_messages = defaultdict[int, list[Message]](list)

   def get_count(self, message : Message) -> int:
      return len(self.album_messages[message.media_group_id])

   def add_album_message(self, message : Message) -> int:
      self.album_messages[message.media_group_id].append(message)
      return self.get_count(message)

   def get_result_album(self, message : Message) -> list[Message]:
      album_messages = self.album_messages.pop(message.media_group_id)
      album_messages.sort(key=lambda m: m.message_id)
      return album_messages

   async def __call__(self,
                      handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                      event: Message,
                      data: Dict[str, Any]) -> Any:
      if event.media_group_id is None:
         return await handler(event, data)
      
      self.album_messages[event.media_group_id].append(event)
      count = self.get_count(event)
      await asyncio.sleep(self.timeout)
      # Ожидаем поступления следующего сообщения
      new_count = self.get_count(event)

      if new_count != count:
         return

      data.update(
         album_messages=self.get_result_album(event),
      )

      return await handler(event, data)


# Middleware для проверки блокировки
class BlockMiddleware(BaseMiddleware):
   async def __call__(
      self,
      handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
      event: TelegramObject,
      data: Dict[str, Any]
   ) -> Any:
      user_id = None

      if "event_from_user" in data and data["event_from_user"]:
         user_id = data["event_from_user"].id

      if str(user_id) in js.get_banned_users():
         return

      return await handler(event, data)