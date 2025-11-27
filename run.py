import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from datetime import datetime
from app.handlers import router
from app.database.models import async_main
from app.handlers import mail_results
from app.middlewares import BlockMiddleware

import app.database.requests as req
import app.utils.json_requests as js
import aioschedule as schedule


load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.update.middleware(BlockMiddleware())


async def main():
   asyncio.create_task(scheduler())
   await async_main()
   dp.include_router(router)
   await dp.start_polling(bot)


# Некоторые задачи, которые должны выполняться по расписанию
async def jobs():
   time = datetime.now()

   if time.month == 5 and time.day == 8: # 8-го мая объявляем о победителях
      await mail_results()
   
   elif time.month == 8 and time.day == 31: # 31-го августа очищаем БД от старых ДЗ + очищаем статистику за уч. год
      await req.remove_all_posts()
      js.clear_hw_count("this_year")

      await bot.send_message(
         chat_id=1149546500,
         text="🗄 Все старые посты удалены из БД."
              "📊 Статистика очищена"
      )


schedule.every().day.at("12:00").do(jobs)


async def scheduler():
   while True:
      await schedule.run_pending()
      await asyncio.sleep(1)


if __name__ == "__main__":
   print("Бот запущен.")
   # logging.basicConfig(level=logging.INFO)

   try:
      asyncio.run(main())
   except KeyboardInterrupt:
      print("Бот остановлен.")