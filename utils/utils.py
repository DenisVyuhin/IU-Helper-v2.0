import os
import constants as con
import app.database.requests as req

from aiogram import Bot
from aiogram.types import Message
from aiogram.enums.input_media_type import InputMediaType
from utils.mistral import mistral_ai, deepseek_ai
from dotenv import load_dotenv

load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"))


# Кодер, преобразует #предмет #неделя #класс -> набор чисел (1.2.3)
# Это я использую для того, чтобы передавать хештеги в callback (а колбэк не принимает более 64 бит)
def code(hashtags: str) -> str:
   tags = hashtags.split("#")
   tags = [i.lower().replace(" ", "") for i in tags if i not in ["", " "]]
   lower_sub = [i.lower() for i in con.school_subject]
   lower_year = [i.lower().replace(" ", "") for i in con.years]
   lower_grades = [i.lower().replace(" ", "") for i in con.grades]
   lower_week = []

   for i in con.weeks:
      for j in i:
         lower_week.append(j.lower().replace(" ", ""))

   if len(tags) == 3:
      id = [
         str(lower_sub.index(tags[0])),
         str(lower_week.index(tags[1])),
         str(lower_grades.index(tags[2]))
      ]
   elif len(tags) == 4:
      id = [
         str(lower_sub.index(tags[0])),
         str(lower_week.index(tags[1])),
         str(lower_year.index(tags[2])),
         str(lower_grades.index(tags[3]))
      ]
   
   return ".".join(id)


# Декодер, преобразует 1.2.3 -> #предмет #неделя #класс
def decode(code: str) -> str:
   id = code.split(".")
   id = [int(i) for i in id]

   lower_sub = [i.lower() for i in con.school_subject]
   lower_year = [i.lower().replace(" ", "") for i in con.years]
   lower_grades = [i.lower().replace(" ", "") for i in con.grades]
   lower_week = []

   for i in con.weeks:
      for j in i:
         lower_week.append(j.lower().replace(" ", ""))

   if len(id) == 3:
      result = f"#{lower_sub[id[0]].lower()} #{lower_week[id[1]].lower()} #{lower_grades[id[2]].lower()}"
   elif len(id) == 4:
      result = f"#{lower_sub[id[0]].lower()} #{lower_week[id[1]].lower()} #{lower_year[id[2]].lower()} #{lower_grades[id[3]].lower()}"
   
   return result


# Получаем хештеги из поста
def get_hashtags(message) -> str:
   text = message.text or message.caption
   entities = message.entities or message.caption_entities
   hashtags = []

   if entities:
      for entity in entities:
         if entity.type == "hashtag":
            hashtag = text[entity.offset : entity.offset + entity.length]
            hashtags.append(hashtag)
   result = " ".join(hashtags)

   return result


# Рассылка
async def mailing(text: str):
   users = [
      await req.get_user_by_id(i+1) for i in range(await req.get_users_count())
   ]

   for user in users:
      try:
         await bot.send_message(
            chat_id=user.tg_id,
            text=text,
            parse_mode="html",
            disable_web_page_preview=True
         )
      except Exception as e:
         print(f"Error: {e}")


# Проверяем подписки пользователя на каналы
async def user_sub_check(user_id, channel_id) -> bool:
   try:
      member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
      status = str(member.status)

      if status in ["member", "administrator", "creator", "owner"]:  # owner - это с новым API
         return True
      else:
         return False
   except Exception as e:
      print("Ошибка при проверке подписки")


# Функция для стилизации текста в нужный формат
async def formatting_post(text: str) -> str:
   try:
      res = await mistral_ai(
         f"Стилизуй первый текст: '{text}' По примеру второго текста: '#русский #28неделя #9класс\n\nОценка 5\n\n<blockquote><b>Комментарий от учителя:</b>\nВы справились с работой, но неверно отметили грамматическую основу в задании 1</blockquote>\n\nРебята, будьте внимательны, задание 5 нужно переформулировать!!'. В начале обязательно должны быть хештеги (3-4) (последовательность хештегов такая - предмет, неделя, (может быть год, если он есть), и в конце класс). После идет оценка. Уже дальше могут быть (а могут и не быть. Зависит от первого текста) комментарии. Их два вида: комментарий учителя (сверху обязательно нужно подписать что это комментарий учителя, а после весь блок с комментарием нужно завернуть в <blockquote></blockquote>) и комментарий от ученика (Сверху его подписывать не нужно. Коммент ученика должен быть обычным текстом). От учителя обычно идут каки-то замечания и т.д. Также комментарии от учителя более официальные (это тебе для того, чтобы ты правильно их распределял). Ты должен отформатировать первый текст также как второй, сохряняя html. Ты должен просто отформатировать первый текст, не меняя его содержимое. В качестве ответа дай готовый, форматированный текст, имеющий нужную html разметку."
      )
   except Exception as e:
      res = await deepseek_ai(
         f"Стилизуй первый текст: '{text}' По примеру второго текста: '#русский #28неделя #9класс\n\nОценка 5\n\n<blockquote><b>Комментарий от учителя:</b>\nВы справились с работой, но неверно отметили грамматическую основу в задании 1</blockquote>\n\nРебята, будьте внимательны, задание 5 нужно переформулировать!!'. В начале обязательно должны быть хештеги (3-4) (последовательность хештегов такая - предмет, неделя, (может быть год, если он есть), и в конце класс). После идет оценка. Уже дальше могут быть (а могут и не быть. Зависит от первого текста) комментарии. Их два вида: комментарий учителя (сверху обязательно нужно подписать что это комментарий учителя, а после весь блок с комментарием нужно завернуть в <blockquote></blockquote>) и комментарий от ученика (Сверху его подписывать не нужно. Коммент ученика должен быть обычным текстом). От учителя обычно идут каки-то замечания и т.д. Также комментарии от учителя более официальные (это тебе для того, чтобы ты правильно их распределял). Ты должен отформатировать первый текст также как второй, сохряняя html. Ты должен просто отформатировать первый текст, не меняя его содержимое. В качестве ответа дай готовый, форматированный текст, имеющий нужную html разметку."
      )
   
   res = res.replace("```html", "").replace("```", "")
   
   return res


def get_media_file_id(message : Message) -> str:
   if message.video:
      return message.video.file_id
   elif message.photo:
      return message.photo[-1].file_id
   elif message.document:
      return message.document.file_id
   else:
      return ""


def get_media_type(message : Message) -> str:
   if message.video:
      return InputMediaType.VIDEO
   elif message.photo:
      return InputMediaType.PHOTO
   elif message.document:
      return InputMediaType.DOCUMENT
   else:
      return ""