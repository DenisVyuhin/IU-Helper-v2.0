import os
import datetime
import dotenv

from typing import Optional
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, ReactionTypeEmoji
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from app.utils.utils import *
from app.utils.mistral import mistral_ai, deepseek_ai
from app.middlewares import TestMiddleware

import app.keyboards as kb
import app.database.requests as req
import constants as con
import app.utils.json_requests as js


dotenv.load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"))
router = Router()
router.message.outer_middleware(TestMiddleware())
# router.message.middleware(BlockMiddleware())


class Homework(StatesGroup):
   # hw_link = State()
   grade = State()
   subject = State()
   quarter = State()
   week = State()
   year = State()

class Post(StatesGroup):
   answers = State()         # Сами ответы (файлы или фото)
   hashtags = State()        # Хештеги
   by_user = State()         # От кого ответы
   rating = State()          # Оценка за ДЗ
   teacher_comment = State() # Комментарий от учителя
   user_comment = State()    # Комментарий от пользователя
   notice_user = State()     # Подписывать ли пользователя
   format_post = State()     # Это состояние уже не нужно

   # Дальше идут те же состояние, но уже предназначенные для изменения
   edit_answers = State()
   edit_hashtags = State()
   edit_rating = State()
   edit_teacher_comment = State()
   edit_user_comment = State()
   edit_notice_user = State()
   edit_format_post = State()


class Decline_Post(StatesGroup):
   hashtags = State()
   user_id = State()
   reason = State()

class Ask_question(StatesGroup):
   user_id = State()
   reason = State()

class Answer(StatesGroup):
   user_id = State()
   answer = State()

class User_card(StatesGroup):
   card_link = State()


class Order(StatesGroup):
   order_type = State() # Тип заказа: Отдельное ДЗ / Четверть / Целый год
   user_link = State()  # Ссылка на профиль пользователя
   grade = State()      # Класс
   quartes = State()    # Кол-во четвертей (если заказ на четверть или год)
   subjects = State()   # Предметы (если заказ на определенное ДЗ)
   login = State()      # Логин от ИУ
   password = State()   # Пароль от ИУ
   comment = State()    # Доп. коммент от пользователя

class OperatorChat(StatesGroup):
   user_id = State()
   user_message = State()
   operator_message = State()


"""@router.message()
async def msg(message : Message):
   await test_find_post(message)

async def test_find_post(message: Message):
    try:
        user_tags = message.text.strip()                         # Берём текст от пользователя
        tags = user_tags.split()                                 # Делим на отдельные теги
        query = " ".join(tags)                                   # Соединяем обратно пробелами

        search_result = await bot.search_chat_messages(
            chat_id=2571306359,
            query=query,
            limit=1
        )                                                        # Ищем 1 результат

        if not search_result.messages:
            await message.answer("Пост с такими хештегами не найден 😔")
            return

        msg = search_result.messages[0]                          # Первый найденный пост
        link = f"https://t.me/IU_9klass/{msg.message_id}"

        await message.answer(f"Нашёл пост:\n{link}")             # Отправляем ссылку пользователю

    except Exception as e:
        await message.answer(f"Ошибка: {e}")
"""
#    try:
#       text = await mistral_ai(str(message.text))
#    except Exception as e:
#       text = await deepseek_ai(str(message.text))
#    await message.reply(text)


@router.message(CommandStart())
async def cmd_start(message : Message, state : FSMContext):
   user_id = message.from_user.id
   me = await bot.get_me()

   try:
      user = await req.get_user(message.from_user.id)
      print(user.tg_id)
   except Exception as e:
      user_link = f"(@{message.from_user.username})" if message.from_user.username else f"\ntg://user?id={message.from_user.id}"
      await message.answer_sticker("CAACAgIAAxkBAAIEnWiKQEH9Ctcf0HWZ_i3hwghVioJQAAJCEAACM8UpSZAO1BGnKkqCNgQ")
      await bot.send_message(
         chat_id=con.reports_chat_id,
         message_thread_id=con.new_people,
         text=f"<b>Новый пользователь!</b>\n\n"
            f"{message.from_user.first_name} {user_link}",
         parse_mode="html"
      )

   await message.reply(
      f"<b>🎄 Привет {message.from_user.first_name}! 🎄</b>\n\n"
      f"Здесь ты найдешь ДЗ, а также сможешь заработать 😉",
      parse_mode="html",
      reply_markup=kb.start_keyboard
   )

   # Отдельное доп-приветствие для "особых" людей
   if user_id in con.exceptional_users:
      await message.reply(f"Привет {con.get_except_name(user_id)}")
      await message.answer_sticker(con.get_except_sticker(user_id))

   await state.clear()
   await req.add_user(message.from_user.id, message.from_user.first_name)
   await req.add_bot_stats(me.id)


@router.message(Command("price"))
async def cmd_price(message : Message, state : FSMContext):
   await state.clear()
   await message.answer(
      f"<b>💸 Прайс:</b>\n\n"
      f"• Письменное ДЗ — {con.dz_price}₽\n"
      f"• КР — {con.kr_price}₽\n"
      f"• АР — {con.ar_price}₽\n"
      f"• Тест — {con.test_price}₽\n\n"
      f"<b>📚 Четверти:</b>\n"
      f"Стоимость зависит от класса, в среднем — 12 000₽\n\n"
      f"<b><i>📝 Переписывание уже входит в стоимость</i></b>",
      parse_mode="html",
      reply_markup=kb.buy_dz_keyboard
   )


@router.message(Command("stats"))
async def cmd_stats(message : Message, state : FSMContext):
   await state.clear()

   win1 = con.winner_price[0]
   win2 = con.winner_price[1]
   win3 = con.winner_price[2]

   await message.answer(
      f"<b>📊 ТОП лучших пользователей</b>\n\n"
      f"<blockquote>"
      f"<b>Призы в конце учебного года:\n\n</b>"
      f"🥇 — <b>{win1}₽</b> ({int(win1/2)} stars)\n"
      f"🥈 — <b>{win2}₽</b> ({int(win2/2)} stars)\n"
      f"🥉 — <b>{win3}₽</b> ({int(win3/2)} stars)"
      f"</blockquote>",
      parse_mode="html",
      reply_markup=kb.stats_keyboard
   )


@router.callback_query(F.data == "top_all_time")
async def cb_top_all_time(callback : CallbackQuery):
   top_list = "\n".join(js.get_users("all_time", 15))

   if top_list == "":
      top_list = "Список пуст..."

   await callback.message.edit_text(
      f"<b>🏆 ТОП пользователей за всё время</b>\n\n"
      f"<i>{top_list}</i>"
      f"\n\n<i>Чтобы оказаться в этом списке, поделись своими ДЗ с помощью команды /post</i>",
      parse_mode="html",
      reply_markup=kb.back_to_stats_keyboard
   )
   await callback.answer()


@router.callback_query(F.data == "top_this_quarter")
async def cb_top_all_time(callback : CallbackQuery):
   top_list = "\n".join(js.get_users("this_year", 15))

   if top_list == "":
      top_list = "Список пуст..."

   await callback.message.edit_text(
      f"<b>🎓 ТОП пользователей за учебный год</b>\n\n"
      f"<i>{top_list}</i>"
      f"\n\n<i>Чтобы оказаться в этом списке, поделись своими ДЗ с помощью команды /post</i>",
      parse_mode="html",
      reply_markup=kb.back_to_stats_keyboard
   )
   await callback.answer()


@router.callback_query(F.data == "back_to_stats")
async def cb_back_to_stats(callback : CallbackQuery):
   win1 = con.winner_price[0]
   win2 = con.winner_price[1]
   win3 = con.winner_price[2]

   await callback.message.edit_text(
      f"<b>📊 ТОП лучших пользователей</b>\n\n"
      f"<blockquote>"
      f"<b>Призы в конце учебного года:\n\n</b>"
      f"🥇 — <b>{win1}₽</b> ({int(win1/2)} stars)\n"
      f"🥈 — <b>{win2}₽</b> ({int(win2/2)} stars)\n"
      f"🥉 — <b>{win3}₽</b> ({int(win3/2)} stars)"
      f"</blockquote>",
      parse_mode="html",
      reply_markup=kb.stats_keyboard
   )
   await callback.answer()


@router.message(Command("operator"))
async def cmd_operator(message : Message, state : FSMContext):
   await state.set_state(OperatorChat.user_message)

   await message.answer(
      "<b>✅ Оператор вызван</b>\n\n"
      "Он ответит в ближайшее время, а пока что напишите ваш вопрос:",
      parse_mode="html",
      reply_markup=kb.cancel_keyboard
   )


@router.message(OperatorChat.user_message)
async def forward_to_group(message: Message, state: FSMContext):
   user = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

   await message.copy_to(
      chat_id=con.reports_chat_id,
      message_thread_id=con.calls,
      reply_markup=await kb.operator_answer_keyboard_builder(message.from_user.id)
   )
   await message.react([ReactionTypeEmoji(emoji="👌")])
   # await state.clear()

   # await bot.send_message(
   #    chat_id=con.reports_chat_id,
   #    message_thread_id=con.calls,
   #    text=f"<b>Вопрос от {user}</b>",
   #    parse_mode="html",
   #    reply_markup=await kb.operator_answer_keyboard_builder(message.from_user.id)
   # )


@router.callback_query(F.data.startswith("operator_answer_"))
async def cb_operator_answer(callback : CallbackQuery, state : FSMContext):
   user_id = int(callback.data.replace("operator_answer_", ""))

   await state.set_state(OperatorChat.user_id)
   await state.update_data(user_id=user_id)
   await state.set_state(OperatorChat.operator_message)

   await callback.message.answer(
      "Ваш ответ:",
      reply_markup=kb.cancel_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("close_chat_"))
async def cb_close_chat(callback : CallbackQuery, state : FSMContext):
   user_id = int(callback.data.replace("close_chat_", ""))

   await state.clear()
   await callback.message.edit_text(
      text="<b>🤝 Диалог окончен</b>",
      parse_mode="html"
   )
   await bot.send_message(
      chat_id=user_id,
      text="<b>🤝 Диалог окончен</b>",
      parse_mode="html"
   )
   await callback.answer()


@router.message(OperatorChat.operator_message)
async def forward_to_user(message : Message, state : FSMContext):
   data = await state.get_data()

   await message.copy_to(
      chat_id=data.get("user_id"),
   )
   await message.react([ReactionTypeEmoji(emoji="👌")])
   await state.clear()


@router.message(Command("faq"))
async def cmd_faq(message : Message, state : FSMContext):
   await state.clear()
   await message.answer(
      "<b>👇 Выберите тему вопроса</b>",
      parse_mode="html",
      reply_markup=kb.theme_question_keyboard
   )


@router.callback_query(F.data.startswith("question_about_bot"))
async def cb_bot_questions(callback : CallbackQuery):
   await callback.message.edit_text(
      "<b>❓ Ваш вопрос</b>",
      parse_mode="html",
      reply_markup=kb.answers_about_bot_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("question_about_iu"))
async def cb_iu_questions(callback : CallbackQuery):
   await callback.message.edit_text(
      "<b>❓ Ваш вопрос</b>",
      parse_mode="html",
      reply_markup=kb.answers_about_iu_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("about_bot_faq_"))
async def cb_bot_answers(callback : CallbackQuery):
   question_id = int(callback.data.replace("about_bot_faq_", ""))-1

   await callback.message.edit_text(
      f"{con.about_bot_answers[question_id]}",
      parse_mode="html",
      disable_web_page_preview=True,
      reply_markup=kb.back_to_bot_answers_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("about_iu_faq_"))
async def cb_iu_answers(callback : CallbackQuery):
   question_id = int(callback.data.replace("about_iu_faq_", ""))-1

   await callback.message.edit_text(
      f"{con.about_iu_answers[question_id]}",
      parse_mode="html",
      disable_web_page_preview=True,
      reply_markup=kb.back_to_iu_answers_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("back_to_bot_questions"))
async def cb_bot_questions(callback : CallbackQuery):
   await callback.message.edit_text(
      "<b>❓ Ваш вопрос</b>",
      parse_mode="html",
      reply_markup=kb.answers_about_bot_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("back_to_iu_questions"))
async def cb_iu_questions(callback : CallbackQuery):
   await callback.message.edit_text(
      "<b>❓ Ваш вопрос</b>",
      parse_mode="html",
      reply_markup=kb.answers_about_iu_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("back_to_theme_question"))
async def cb_bot_questions(callback : CallbackQuery):
   await callback.message.edit_text(
      "<b>👇 Выберите тему вопроса</b>",
      parse_mode="html",
      reply_markup=kb.theme_question_keyboard
   )
   await callback.answer()


@router.message(Command("ban"))
async def cmd_banned(message : Message, command : CommandObject, state : FSMContext):
   await state.clear()

   if message.from_user.id == con.owner_id:
      user_id = command.args
      name = "null"

      try:
         user_chat = await bot.get_chat(user_id)
         name = user_chat.first_name
      except Exception as e:
         print("Пользователя нет")

      if user_id:
         js.ban_user(user_id)
         print(js.get_banned_users())

         await message.answer(
            f"<b>🛡 Забанен</b>\n"
            f"{name}",
            parse_mode="html"
         )
      else:
         await message.answer(f"ID не указан")


@router.message(Command("unban"))
async def cmd_unbanned(message : Message, command : CommandObject, state : FSMContext):
   await state.clear()

   if message.from_user.id == con.owner_id:
      user_id = command.args
      name = "null"

      try:
         user_chat = await bot.get_chat(user_id)
         name = user_chat.first_name
      except Exception as e:
         print("Пользователя нет")

      if user_id:
         js.unban_user(user_id)
         print(js.get_banned_users())

         await message.answer(
            f"<b>🛡 Разбанен</b>\n"
            f"{name}",
            parse_mode="html"
         )
      else:
         await message.answer(f"ID не указан")


@router.message(Command("search"))
async def cmd_search(message : Message, state : FSMContext):
   await state.set_state(Homework.grade)
   
   # Проверка на то, есть ли пользователь ХОТЯ БЫ в одном канале
   is_subscribe = bool(
      True in [await user_sub_check(message.from_user.id, i) for i in con.channels_id_for_subscribe]
   )
   
   if not is_subscribe:
      await message.answer(
         "Для поиска ДЗ, нужно подписаться на <b>ОДИН ЛЮБОЙ</b> из этих каналов:\n\n"
         "<a href='https://t.me/IU_9klass'>Ответы 9 класс</a>\n"
         "или\n"
         "<a href='https://t.me/IU_10_klass'>Ответы 10 класс</a>\n",
         parse_mode="html",
         reply_markup=kb.subscribe_keyboard,
         disable_web_page_preview=True
      )
   else:
      await message.answer(
         "<b>🎓 Выберите класс</b>",
         parse_mode="html",
         reply_markup=await kb.grades_keyboard_builder("search")
      )


@router.callback_query(F.data.startswith("grade_search_"))
async def cb_grade(callback : CallbackQuery, state : FSMContext):
   select_grade = callback.data.replace("grade_search_", "").replace(" ", "").lower()

   await state.update_data(grade=select_grade)
   await state.set_state(Homework.subject)

   await callback.message.edit_text(
      "<b>📚 Выберите предмет</b>",
      parse_mode="html",
      reply_markup=await kb.subjects_keyboard_builder("search")
   )
   await callback.answer()


@router.callback_query(F.data.startswith("back_to_grades_search"))
async def cb_back_to_grades(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Homework.grade)
   await callback.message.edit_text(
      "<b>🎓 Выберите класс</b>",
      parse_mode="html",
      reply_markup=await kb.grades_keyboard_builder("search")
   )
   await callback.answer()


@router.callback_query(F.data.startswith("subject_search_"))
async def cb_subject(callback : CallbackQuery, state : FSMContext):
   select_subject = callback.data.replace("subject_search_", "").replace(" ", "").lower()
   
   await state.update_data(subject=select_subject)
   await state.set_state(Homework.quarter)

   await callback.message.edit_text(
      "<b>📆 Выберите четверть</b>",
      parse_mode="html",
      reply_markup=await kb.quarters_keyboard_builder("search")
   )
   await callback.answer()


@router.callback_query(F.data == "back_to_subjects_search")
async def cb_back_to_subjects(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Homework.subject)
   await callback.message.edit_text(
      "<b>📚 Выберите предмет</b>",
      parse_mode="html",
      reply_markup=await kb.subjects_keyboard_builder("search")
   )
   await callback.answer()


@router.callback_query(F.data.startswith("quarter_search_"))
async def cb_quarter(callback : CallbackQuery, state : FSMContext):
   select_squarter = int(callback.data.replace("quarter_search_", "").replace(" четверть", ""))

   await state.update_data(quarter=select_squarter)
   await state.set_state(Homework.week)

   await callback.message.edit_text(
      "<b>📆 Выберите неделю</b>",
      parse_mode="html",
      reply_markup=await kb.weeks_keyboard_builder(select_squarter, "search")
   )
   await callback.answer()


@router.callback_query(F.data == "back_to_quarters_search")
async def cb_back_to_quarters(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Homework.quarter)
   await callback.message.edit_text(
      "<b>📆 Выберите четверть</b>",
      parse_mode="html",
      reply_markup=await kb.quarters_keyboard_builder("search")
   )
   await callback.answer()


@router.callback_query(F.data.startswith("week_search_"))
async def cb_week(callback : CallbackQuery, state : FSMContext):
   select_week = callback.data.replace("week_search_", "").replace(" ", "").lower()
   me = await bot.get_me()

   await state.update_data(week=select_week)
   data = await state.get_data()

   if data["subject"] == "немецкий" or data["subject"] == "китайский":
      await state.set_state(Homework.year)
      await callback.message.edit_text(
         "<b>📌 Выберите год</b>",
         parse_mode="html",
         reply_markup=await kb.years_keyboard_builder("search")
      )
   else:
      tags = f'{data["subject"]}{data["week"]}{data["grade"]}'
      ps = await req.get_posts_url(tags)
      urls = "\n\n".join([p.url for p in ps])

      if ps:
         await callback.message.edit_text(
            f"<b>✅ Ответы найдены</b>\n\n{urls}",
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=kb.search_keyboard
         )
         await req.add_find_posts(me.id)
      else:
         await callback.message.edit_text(
            "<b>😕 Ответы не найдены</b>\n\n"
            "Но вы можете заказать у @KodersUp",
            parse_mode="html",
            reply_markup=kb.try_search_again_keyboard
         )
   await callback.answer()


@router.callback_query(F.data == "back_to_weeks_search")
async def cb_back_to_weeks(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Homework.week)

   data = await state.get_data()
   quarter = data.get("quarter", 1)  # По умолчанию первая четверть

   await callback.message.edit_text(
      "<b>📆 Выберите неделю</b>",
      parse_mode="html",
      reply_markup=await kb.weeks_keyboard_builder(quarter, "search")
   )
   await callback.answer()


@router.callback_query(F.data.startswith("year_search_"))
async def cb_year(callback : CallbackQuery, state : FSMContext):
   select_year = callback.data.replace("year_search_", "").replace(" ", "").lower()
   me = await bot.get_me()

   await state.update_data(year=select_year)
   data = await state.get_data()
   
   tags = f'{data["subject"]}{data["week"]}{data["year"]}{data["grade"]}'
   ps = await req.get_posts_url(tags)
   urls = "\n\n".join([p.url for p in ps])

   if ps:
      await callback.message.edit_text(
         f"<b>✅ Ответы найдены</b>\n\n{urls}",
         parse_mode="html",
         disable_web_page_preview=True,
         reply_markup=kb.search_keyboard
      )
      await req.add_find_posts(me.id)
   else:
      await callback.message.edit_text(
         "<b>😕 Ответы не найдены</b>\n\n"
         "Но вы можете заказать у @KodersUp",
         parse_mode="html",
         reply_markup=kb.try_search_again_keyboard
      )
   await callback.answer()


# @router.message(Homework.hw_link)
# async def msg_hw_link(message : Message, state : FSMContext):
#    me = await bot.get_me()
#    msg = await message.answer("<b>Ищу...</b>", parse_mode="html")
   
#    # С помощью нейронки определяем хештеги
#    res = await mistral_ai(f"Из данного сообщения: '{message.text}', постарайся составить 3 хештега (иногда нужно 4). А именно #предмет\n#<число>неделя\n#<число>год (такой хештег нужен только с немецким. С другими предметами год не нужен)\n#<число>класс. Имей ввиду, что в сообщении может быть написан лишь предмет, и несколько чисел, поэтому каждое число бери по своему порядку - неделя, возможно год, класс. Все хештеги должны быть без пробелов. Вот все возможные предметы - {','.join(con.school_subject)} (ВиС -  вероятность и статистика). В качестве ответа, дай лишь хештеги, и в таком порядке (предмет, неделя, год (если есть), класс) (просто 3-4 хештега, ничего более)")
#    res = res.replace("\n", "").replace("#", "").lower()
#    ps = await req.get_post_url(res)
   
#    if ps:
#       await msg.edit_text(
#          f"<b>✅ Ответы найдены</b>\n\n{ps.url}",
#          parse_mode="html",
#          disable_web_page_preview=True,
#          reply_markup=kb.search_keyboard
#       )
#       await req.add_find_posts(me.id)
#    else:
#       await msg.edit_text(
#          "<b>😕 Ответы не найдены</b>\n\n"
#          "Но вы можете заказать у @KodersUp",
#          parse_mode="html"
#       )
#    await state.clear()


@router.message(Command("bot"))
async def cmd_stats(message : Message, state : FSMContext):
   await state.clear()

   me = await bot.get_me()
   bot_stats = await req.get_bot_info(me.id)

   if message.from_user.id == con.owner_id:
      await message.answer(
         f"<b>🤖 Статистика бота:</b>\n\n"
         f"👤 Пользователей: {await req.get_users_count()}\n"
         f"🔍 Найденных ДЗ: {bot_stats.find_posts}\n"
         f"📣 Выложенных ДЗ: {bot_stats.published_posts}\n"
         f"💰 Выведенных звезд: {bot_stats.debit_stars} ≈ {bot_stats.debit_stars*2}₽\n"
         f"⛔️ Забаненых: {len(js.get_banned_users())}",
         parse_mode="html"
      )


@router.message(Command("post"))
async def cmd_post(message : Message, state : FSMContext):
   await state.clear()
   await state.set_state(Post.answers)

   await message.answer(
      "<b>Шаг 1/5. ✅☑️☑️☑️☑️</b>\n\n"
      "Отправьте ответы на ДЗ (фото, видео или файлы)\n\n"
      "<blockquote>До 10 файлов (фото или видео) в одном посте. Если файлов больше – сделайте два поста: первый с 10 файлами, второй с оставшимися.</blockquote>",
      parse_mode="html",
      reply_markup=kb.cancel_keyboard
   )


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback : CallbackQuery, state : FSMContext):
   await state.clear()
   await callback.message.delete()
   await callback.answer()


@router.message(Post.answers)
async def get_post(message : Message, state : FSMContext, album_messages : Optional[list[Message]] = None):
   if not (message.photo or message.document or message.video):
      await message.answer("😕 Такие ответы не подходят. Нужны фотографии/видео или файлы")
   else:
      await state.set_state(Post.answers)
      if album_messages:
         await state.update_data(answers=album_messages)
      else:
         await state.update_data(answers=message)
      await state.set_state(Post.hashtags)

      await message.answer(
         "<b>Шаг 2/5. ✅✅☑️☑️☑️</b>\n\n"
         "Напишите предмет, неделю и класс (можно год, если это немецкий или китайский)",
         parse_mode="html"
      )


@router.message(Post.hashtags, F.text)
async def msg_hashtags(message : Message, state : FSMContext):
   msg = await message.answer("Секунду...")

   try:
      tags = await mistral_ai(f"Из сообщения: '{message.text}', составь 3 хештега (иногда нужно 4), в таком формате #предмет #<число>неделя #<число>год (такой хештег нужен только с немецким и с китайским. С другими предметами год не нужен) #<число>класс. В сообщении может быть написан лишь предмет, и несколько чисел, поэтому каждое число бери по своему порядку - неделя, возможно год, класс. Все хештеги должны быть без пробелов. Предметы ТОЛЬКО из списка: {','.join(con.school_subject)}. (ВиС -  вероятность и статистика). Хештег с предметом должен быть такой же, как в приведенном списке. Года ТОЛЬКО из списка: {con.years}. Ответы должен состоять ТОЛЬКО из 3-4 хештегов (в порядке: #предмет #неделя, #год (если есть) #класс) без лишнего текста.")
   except Exception as e:
      tags = await deepseek_ai(f"Из сообщения: '{message.text}', составь 3 хештега (иногда нужно 4), в таком формате #предмет #<число>неделя #<число>год (такой хештег нужен только с немецким и с китайским. С другими предметами год не нужен) #<число>класс. В сообщении может быть написан лишь предмет, и несколько чисел, поэтому каждое число бери по своему порядку - неделя, возможно год, класс. Все хештеги должны быть без пробелов. Предметы ТОЛЬКО из списка: {','.join(con.school_subject)}. (ВиС -  вероятность и статистика). Хештег с предметом должен быть такой же, как в приведенном списке. Года ТОЛЬКО из списка: {con.years}. Ответы должен состоять ТОЛЬКО из 3-4 хештегов (в порядке: #предмет #неделя, #год (если есть) #класс) без лишнего текста.")
   
   tags = tags.replace("\n", " ").lower()
   username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

   await state.update_data(hashtags=tags)

   await state.set_state(Post.by_user)
   await state.update_data(by_user=f"Ответы от {username}")
   
   await state.set_state(Post.rating)
   await msg.edit_text(
      "<b>Шаг 3/5. ✅✅✅☑️☑️</b>\n\n"
      "Укажите оценку за ДЗ",
      parse_mode="html",
      reply_markup=await kb.rating_keyboard_builder()
   )


# Тут должен быть колбэк-хендлер на нажатие кнопки с оценками, но она будет ниже (на 450-550 строке, примерно)


@router.callback_query(F.data == "skip_teacher_comment")
async def cb_skip_teacher_comment(callback : CallbackQuery, state : FSMContext):
   await state.update_data(teacher_comment="")
   await state.set_state(Post.user_comment)
   
   await callback.message.edit_text(
      "<b>Шаг 5/5. ✅✅✅✅✅</b>\n\n"
      "Напишите личный комментарий от себя (это могут быть предупреждения, пожеланий и т.п.)",
      parse_mode="html",
      reply_markup=kb.skip_user_comment_keyboard
   )
   await callback.answer()


@router.message(Post.teacher_comment, F.text)
async def msg_teacher_comment(message : Message, state : FSMContext):
   await state.update_data(teacher_comment=message.text)
   await state.set_state(Post.user_comment)
   
   await message.answer(
      "<b>Шаг 5/5. ✅✅✅✅✅</b>\n\n"
      "Напишите личный комментарий от себя (это могут быть предупреждения, пожеланий и т.п.)",
      parse_mode="html",
      reply_markup=kb.skip_user_comment_keyboard
   )


@router.callback_query(F.data == "skip_user_comment")
async def cb_skip_teacher_comment(callback : CallbackQuery, state : FSMContext):
   await state.update_data(user_comment="")

   data = await state.get_data()

   try:
      post = await create_post(data)
      await callback.message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)

   await callback.message.answer(
      "<b>Пост успешно создан</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )
   await callback.answer()


@router.message(Post.user_comment, F.text)
async def msg_user_comment(message : Message, state : FSMContext):
   await state.update_data(user_comment=message.text)

   data = await state.get_data()

   try:
      post = await create_post(data)
      await message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)

   await message.answer(
      "<b>Пост успешно создан</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )


@router.callback_query(F.data == "edit_post")
async def cb_edit_post(callback : CallbackQuery, state : FSMContext):
   data = await state.get_data()
   user = data.get("by_user", "")

   await callback.message.edit_text(
      "Что хотите отредактировать?",
      reply_markup=await kb.edit_options_keyboard_builder(user=="")
   )
   await callback.answer()


@router.callback_query(F.data.startswith("edit_user_"))
async def cb_edit_by_user(callback : CallbackQuery, state : FSMContext):
   user_is_hidden = callback.data.replace("edit_user_", "") == "True"
   # print(callback.data)
   # print(user_is_hidden)
   hidden = not user_is_hidden # Обратное значение (True -> False, False -> True)
   # print(hidden)

   await state.set_state(Post.by_user)

   if hidden == False: # Если нужно показать имя
      username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
      await state.update_data(by_user=f"Ответы от {username}")
   else: # Если нужно скрыть имя
      await state.update_data(by_user="")
      

   data = await state.get_data()
   
   try:
      post = await create_post(data)
      await callback.message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)
   
   await callback.message.answer(
      "<b>Пост успешно изменен</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )
   await callback.answer()


@router.callback_query(F.data == "back_to_edit_options")
async def cb_back_to_edit_options(callback : CallbackQuery):
   await callback.message.edit_text(
      "<b>Пост успешно создан</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )
   await callback.answer()


# --------------------------------------------------
# ВСЕ ОБРАБОТЧИКИ ДЛЯ РЕДАКТИРОВАНИЯ ПОСТА
# --------------------------------------------------

# Пользователь нажимает на "изменить медиа"
@router.callback_query(F.data == "edit_media")
async def cb_edit_user_comment(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Post.edit_answers)
   await callback.message.answer(
      "Отправьте новые ответы на ДЗ (фото, видео или файлы)\n\n"
      "<blockquote>До 10 файлов (фото или видео) в одном посте. Если файлов больше – сделайте два поста: первый с 10 файлами, второй с оставшимися.</blockquote>",
      parse_mode="html",
   )
   await callback.answer()


# Приинимаем новые медиа
@router.message(Post.edit_answers)
async def msg_new_media(message : Message, state : FSMContext, album_messages : Optional[list[Message]] = None):
   if not (message.photo or message.document or message.video):
      await message.answer("😕 Такие ответы не подходят. Нужны фотографии/видео или файлы")
   else:
      if album_messages:
         await state.update_data(answers=album_messages)
      else:
         await state.update_data(answers=message)
      
   data = await state.get_data()
   
   try:
      post = await create_post(data)
      await message.answer_media_group(post)
   except Exception as e:
      await answer_one_media_post(data, message)
   
   await message.answer(
      "<b>Пост успешно изменен</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )

# Пользователь нажимает на "изменить хештеги"
@router.callback_query(F.data == "edit_hashtags")
async def cb_edit_hashtags(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Post.edit_hashtags)
   await callback.message.answer("Напишите предмет, неделю и класс (можно год, если это немецкий или китайский)")
   await callback.answer()


# Принимаем новые хештеги
@router.message(Post.edit_hashtags, F.text)
async def msg_new_hashtags(message : Message, state : FSMContext):
   try:
      tags = await mistral_ai(f"Из сообщения: '{message.text}', составь 3 хештега (иногда нужно 4), в таком формате #предмет #<число>неделя #<число>год (такой хештег нужен только с немецким и с китайским. С другими предметами год не нужен) #<число>класс. В сообщении может быть написан лишь предмет, и несколько чисел, поэтому каждое число бери по своему порядку - неделя, возможно год, класс. Все хештеги должны быть без пробелов. Предметы ТОЛЬКО из списка: {','.join(con.school_subject)}. (ВиС -  вероятность и статистика). Хештег с предметом должен быть такой же, как в приведенном списке. Года ТОЛЬКО из списка: {con.years}. Ответы должен состоять ТОЛЬКО из 3-4 хештегов (в порядке: #предмет #неделя, #год (если есть в сообщении) #класс) без лишнего текста.")
   except Exception as e:
      tags = await deepseek_ai(f"Из сообщения: '{message.text}', составь 3 хештега (иногда нужно 4), в таком формате #предмет #<число>неделя #<число>год (такой хештег нужен только с немецким и с китайским. С другими предметами год не нужен) #<число>класс. В сообщении может быть написан лишь предмет, и несколько чисел, поэтому каждое число бери по своему порядку - неделя, возможно год, класс. Все хештеги должны быть без пробелов. Предметы ТОЛЬКО из списка: {','.join(con.school_subject)}. (ВиС -  вероятность и статистика). Хештег с предметом должен быть такой же, как в приведенном списке. Года ТОЛЬКО из списка: {con.years}. Ответы должен состоять ТОЛЬКО из 3-4 хештегов (в порядке: #предмет #неделя, #год (если есть в сообщении) #класс) без лишнего текста.")
   tags = tags.replace("\n", " ").lower()

   await state.update_data(hashtags=tags)

   data = await state.get_data()
   
   try:
      post = await create_post(data)
      await message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)
   
   await message.answer(
      "<b>Пост успешно изменен</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )


# Пользователь нажимает на "изменить оценку"
@router.callback_query(F.data == "edit_rating")
async def cb_edit_rating(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Post.edit_rating)
   await callback.message.answer("Укажите оценку за ДЗ", reply_markup=await kb.rating_keyboard_builder())
   await callback.answer()


# Принимаем новую оценку
@router.callback_query(Post.edit_rating, F.data.startswith("rating_"))
async def cb_new_hashtags(callback : CallbackQuery, state : FSMContext):
   rating = int(callback.data.replace("rating_", ""))
   await state.update_data(rating=rating)

   data = await state.get_data()
   
   try:
      post = await create_post(data)
      await callback.message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)
   
   await callback.message.answer(
      "<b>Пост успешно изменен</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )
   await callback.answer()


# Пользователь нажимает на "изменить комментарий учителя"
@router.callback_query(F.data == "edit_teacher_comment")
async def cb_edit_teacher_comment(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Post.edit_teacher_comment)
   await callback.message.answer("Напишите комментарий учителя")
   await callback.answer()


# Принимаем новый комментарий учителя
@router.message(Post.edit_teacher_comment, F.text)
async def msg_new_teacher_comment(message : Message, state : FSMContext):
   await state.update_data(teacher_comment=message.text)

   data = await state.get_data()
   
   try:
      post = await create_post(data)
      await message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)
   
   await message.answer(
      "<b>Пост успешно изменен</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )


# Пользователь нажимает на "изменить комментарий пользователя"
@router.callback_query(F.data == "edit_user_comment")
async def cb_edit_user_comment(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Post.edit_user_comment)
   await callback.message.answer("Напишите личный комментарий от себя (это могут быть предупреждения, пожеланий и т.п.)")
   await callback.answer()


# Принимаем новый комментарий пользователя
@router.message(Post.edit_user_comment, F.text)
async def msg_new_user_comment(message : Message, state : FSMContext):
   await state.update_data(user_comment=message.text)

   data = await state.get_data()
   
   try:
      post = await create_post(data)
      await message.answer_media_group(post)
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg)
   
   await message.answer(
      "<b>Пост успешно изменен</b>\n\n"
      "🕹 Опции",
      parse_mode="html",
      reply_markup=kb.edit_post_keyboard
   )


# ЗАВЕРШЕНИЕ СОЗДАНИЯ ПОСТА
@router.callback_query(F.data == "ready_post")
async def cb_ready_post(callback : CallbackQuery, state : FSMContext):
   data = await state.get_data()
   hashtags = data["hashtags"]
   # print(hashtags)

   try:
      post = await create_post(data)
      await bot.send_media_group(
         chat_id=con.reports_chat_id,
         message_thread_id=con.offers,
         media=post,
      )
   except Exception as e:
      msg = data["answers"]
      await answer_one_media_post(data, msg, con.reports_chat_id)
   
   tags = f'{hashtags.replace(" ", "").replace("#", "")}'
   ps = await req.get_post_url(tags)

   text = []

   if ps:
      text.append(f"<b>⚠️ Подобное ДЗ уже существует:</b>\n{ps.url}\n")
   
   text.append("🕹 Действия с постом")
   text = "\n".join(text)

   await bot.send_message(
      chat_id=con.reports_chat_id,
      message_thread_id=con.offers,
      text=text,
      parse_mode="html",
      disable_web_page_preview=True,
      reply_markup=await kb.post_keyboard_builder(callback.from_user.id, hashtags)
   )

   await state.clear()
   await callback.message.edit_text(
      "⌛️ Ожидайте проверки",
      reply_markup=kb.open_menu_keyboard
   )
   await callback.answer()


@router.callback_query(F.data == "remove_post")
async def cb_remove_post(callback : CallbackQuery, state : FSMContext):
   await state.clear()
   await callback.message.edit_text(
      "🗑️ Пост успешно удален.",
      reply_markup=kb.open_menu_keyboard
   )
   await callback.answer()


@router.message(Command("profile"))
async def cmd_profile(message : Message, state : FSMContext):
   user = await req.get_user(message.from_user.id)
   
   await state.clear()

   await message.answer(
      f"🎅 <b>Это ваш профиль</b>\n"
      f"ID: {message.from_user.id}\n\n"
      f"<b>Статистика:</b>\n"
      f"Ваши ДЗ: {user.posts}\n\n"
      f"<b>Баланс:</b>\n"
      f"⭐️ {user.stars} ≈ {user.stars*2}₽",
      parse_mode="html",
      reply_markup=kb.profile_keyboard
   )


@router.callback_query(F.data == "open_profile")
async def cb_profile(callback : CallbackQuery):
   user = await req.get_user(callback.from_user.id)

   await callback.message.answer(
      f"🎅 <b>Это ваш профиль</b>\n"
      f"ID: {callback.from_user.id}\n\n"
      f"<b>Статистика:</b>\n"
      f"Ваши ДЗ: {user.posts}\n\n"
      f"<b>Баланс:</b>\n"
      f"⭐️ {user.stars} ≈ {user.stars*2}₽",
      parse_mode="html",
      reply_markup=kb.profile_keyboard
   )
   await callback.answer()


@router.channel_post()
async def new_post(message : Message):
   channels_id = [
      -1002592375904,
      -1002762908626,
      -1002571306359,
      -1002750671779,
      -1002783651099,
      -1002986782966
   ]
   
   is_my_channel = message.chat.id in channels_id

   x = datetime.datetime.now()
   default_tags = get_hashtags(message)
   tags = default_tags.replace("#", "").replace(" ", "").lower()

   if default_tags:
      try:
         normal_hashtags = await mistral_ai(
            f"входящие хештеги: {default_tags} Эти хештеги преобразуй в формат: #предмет #<число>неделя #<число>год #<число>класс. Предметы ТОЛЬКО из списка: {con.school_subject}. Хештег #<>год нужен только в том случае, если во входящих хештегах есть #китайский ИЛИ #немецкий, в остальных случая хештег с годом не нужен. В качестве ответа дай 3 (если есть немецкий или китайский, то 4) хештега, без лишнего текста."
         )
      except Exception as e:
         normal_hashtags = await deepseek_ai(
            f"входящие хештеги: {default_tags} Эти хештеги преобразуй в формат: #предмет #<число>неделя #<число>год #<число>класс. Предметы ТОЛЬКО из списка: {con.school_subject}. Хештег #<>год нужен только в том случае, если во входящих хештегах есть #китайский ИЛИ #немецкий, в остальных случая хештег с годом не нужен. В качестве ответа дай 3 (если есть немецкий или китайский, то 4) хештега, без лишнего текста."
         )

      if normal_hashtags:
         normal_hashtags = normal_hashtags.replace("\n", " ").lower()
         tags = normal_hashtags.replace("#", "").replace(" ", "")

   if is_my_channel:
      url = f"https://t.me/{message.chat.username}/{message.message_id}"

      await req.add_post(
         message.message_id,
         f"{message.chat.username}_{message.message_id}",
         tags,
         url
      )

      if tags:
         await bot.send_message(
            chat_id=con.reports_chat_id,
            text=
            f"<b>Опубликован пост</b>\n"
            f"{x.strftime('%d.%m.%Y в %X')}\n\n"
            f"<b>Хештеги:</b>\n"
            f"{default_tags}\n{normal_hashtags}\n\n"
            f"<b>Key поста:</b>\n"
            f"<pre>{message.chat.username}_{message.message_id}</pre>\n\n",
            parse_mode="html",
            message_thread_id=con.new_posts
         )
   # else:
   #    if tags:
   #       await bot.send_message(
   #          chat_id=con.reports_chat_id,
   #          text=
   #          f"<b>Попытка публикации</b>\n"
   #          f"{x.strftime('%d.%m.%Y в %X')}\n\n"
   #          f"<b>ID канала:</b>\n"
   #          f"{message.chat.id}\n\n"
   #          f"<b>Хештеги:</b>\n"
   #          f"{default_tags}\n\n"
   #          f"<b>Key поста:</b>\n"
   #          f"<pre>{message.chat.username}_{message.message_id}</pre>\n\n",
   #          parse_mode="html",
   #          message_thread_id=con.new_posts
   #       )


@router.message(Command("remove"))
async def cmd_remove(message : Message, command : CommandObject, state : FSMContext):
   await state.clear()

   key = command.args
   
   if message.from_user.id == con.owner_id:
      try:
         await req.remove_post(key)
         await message.answer("✅ Пост удален")
      except Exception as e:
         await message.answer(f"Ошибка: {e}")


@router.message(Command("debit"))
async def cmd_debit_money(message : Message, command : CommandObject, state : FSMContext):
   await state.clear()

   me = await bot.get_me()

   if message.from_user.id == con.owner_id:
      try:
         user = await req.get_user(command.args) # Получаем пользователя
         amount_stars = user.stars               # И его кол-во звезд

         await req.add_debit_stars(me.id, amount_stars) # Перед тем как списать звезды, записываем сумму звезд в статистику
         await req.clear_stars(command.args)            # А далее списываем звезды со счета
         await message.answer("✅ Деньги списаны")
         await bot.send_message(
            chat_id=command.args,
            text="✅ Деньги отправлены на вашу карту"
         )
      except Exception as e:
         await message.answer(f"Ошибка: {e}")


# --------------------------------------------------
# ОБРАБОТЧИКИ КНОПОК (тут не все обработчики кнопок, сверху еще есть)
# --------------------------------------------------


@router.callback_query(F.data.startswith("rating_"))
async def cb_rating(callback : CallbackQuery, state : FSMContext):
   rating = int(callback.data.replace("rating_", ""))

   await state.update_data(rating=rating)
   await state.set_state(Post.teacher_comment)
   
   await callback.message.answer(
      "<b>Шаг 4/5. ✅✅✅✅☑️</b>\n\n"
      "Напишите комментарий от учителя",
      parse_mode="html",
      reply_markup=kb.skip_teacher_comment_keyboard if rating >= 4 else None
   )

   await callback.answer()


@router.callback_query(F.data == "open_menu")
async def cb_open_menu(callback : CallbackQuery, state : FSMContext):
   await state.clear()
   await callback.message.answer(
      f"<b>📱 Выберите действие</b>",
      parse_mode="html",
      reply_markup=kb.start_keyboard
   )
   await callback.answer()


@router.callback_query(F.data == "buy_dz")
async def cb_buy_dz(callback : CallbackQuery):
   if callback.from_user.id == con.owner_id:
      await callback.message.answer(
         "<b>📚 Заказ</b>\n\n"
         "Что хотите заказать?:",
         parse_mode="html",
         reply_markup=kb.order_type_keyboard
      )

      await callback.answer()
   else:
      await callback.answer("🛠 Будет готово 7 сентября", show_alert=True)


@router.callback_query(F.data.startswith("order_type_"))
async def cb_order_type(callback : CallbackQuery, state : FSMContext):
   type = int(callback.data.replace("order_type_", ""))

   await state.set_state(Order.order_type)
   await state.update_data(order_type=type)
   
   if type == 1:
      await state.set_state(Order.grade)
      await callback.message.edit_text(
         "🎓 Выберите класс:",
         reply_markup=await kb.grades_keyboard_builder("buy_type_1")
      )

   await callback.answer()


@router.callback_query(F.data == "back_to_order_type")
async def cb_back_to_order_type(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Order.order_type)
   await callback.message.edit_text(
      "<b>📚 Заказ</b>\n\n"
      "Что хотите заказать?:",
      parse_mode="html",
      reply_markup=kb.order_type_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("grade_buy_type_1_"))
async def cb_grade_buy_type_1(callback : CallbackQuery, state : FSMContext):
   grade = int(callback.data.replace("grade_buy_type_1_", "").replace(" класс", ""))

   await state.update_data(grade=grade)
   await state.set_state(Order.subjects)
   await callback.message.edit_text(
      "📝 Напишите список предметов и недель, которые хотите заказать.\n\n"
      "<blockquote><b>Например:</b>\n"
      "алгебра 1, 2, 3\n"
      "информатика 4, 5, 6</blockquote>",
      parse_mode="html",
      reply_markup=kb.back_to_select_grade_keyboard
   )
   await callback.answer()


@router.callback_query(F.data == "back_to_grades_buy_type_1")
async def cb_back_to_grades_buy_type_1(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Order.grade)
   await callback.message.edit_text(
      "🎓 Выберите класс:",
      reply_markup=await kb.grades_keyboard_builder("buy_type_1")
   )
   await callback.answer()


@router.message(Order.subjects, F.text)
async def msg_subjects(message : Message, state : FSMContext):
   msg = await message.answer("Секунду...")

   try:
      subs = await mistral_ai(f"Исходное сообщение: {message.text}.Смотри, это сообщение тебе нужно преобразовать в список из предметов и их недель. Каждая новая строка это предмет и перечисление недель через запятую. Пример:\n'Информатика 1, 2, 3\nАлгебра 4, 5, 6' и т.п. В качестве ответа дай ТОЛЬКО готовый список")
   except Exception as e:
      subs = await deepseek_ai(f"Исходное сообщение: {message.text}.Смотри, это сообщение тебе нужно преобразовать в список из предметов и их недель. Каждая новая строка это предмет и перечисление недель через запятую. Пример:\n'Информатика 1, 2, 3\nАлгебра 4, 5, 6' и т.п. В качестве ответа дай ТОЛЬКО готовый список")

   await state.update_data(subjects=subs)

   data = await state.get_data()
   result_price = len(subs.split("\n"))*350

   await msg.edit_text(
      f"<b>📚 Заказ:</b>\n\n"
      f"<b>{data.get('grade')} класс:</b>\n"
      f"{data.get('subjects')}\n\n"
      f"<b>Итого:</b>\n"
      f"{result_price}₽",
      parse_mode="html"
   )


@router.callback_query(F.data == "stats")
async def cb_stats(callback : CallbackQuery):
   win1 = con.winner_price[0]
   win2 = con.winner_price[1]
   win3 = con.winner_price[2]

   await callback.message.answer(
      f"<b>📊 ТОП лучших пользователей</b>\n\n"
      f"<blockquote>"
      f"<b>Призы в конце учебного года:\n\n</b>"
      f"🥇 — <b>{win1}₽</b> ({int(win1/2)} stars)\n"
      f"🥈 — <b>{win2}₽</b> ({int(win2/2)} stars)\n"
      f"🥉 — <b>{win3}₽</b> ({int(win3/2)} stars)"
      f"</blockquote>",
      parse_mode="html",
      reply_markup=kb.stats_keyboard
   )

   await callback.answer()


@router.callback_query(F.data == "search_dz")
async def cb_search_dz(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Homework.grade)
   
   # Проверка на то, есть ли пользователь ХОТЯ БЫ в одном канале
   is_subscribe = bool(
      True in [await user_sub_check(callback.from_user.id, i) for i in con.channels_id_for_subscribe]
   )
   
   if not is_subscribe:
      await callback.message.answer(
         "Для поиска ДЗ, нужно подписаться на <b>ОДИН ЛЮБОЙ</b> из этих каналов:\n\n"
         "<a href='https://t.me/IU_9klass'>Ответы 9 класс</a>\n"
         "или\n"
         "<a href='https://t.me/IU_10_klass'>Ответы 10 класс</a>\n",
         parse_mode="html",
         reply_markup=kb.subscribe_keyboard,
         disable_web_page_preview=True
      )
   else:
      await callback.message.answer(
         "<b>🎓 Выберите класс</b>",
         parse_mode="html",
         reply_markup=await kb.grades_keyboard_builder("search")
      )
   
   await callback.answer()


@router.callback_query(F.data == "offer_dz")
async def cb_offer_dz(callback : CallbackQuery, state : FSMContext):
   await state.clear()
   await state.set_state(Post.answers)

   await callback.message.answer(
      "<b>Шаг 1/5. ✅☑️☑️☑️☑️</b>\n\n"
      "Отправьте ответы на ДЗ (фото, видео или файлы)\n\n"
      "<blockquote>До 10 файлов (фото или видео) в одном посте. Если файлов больше – сделайте два поста: первый с 10 файлами, второй с оставшимися.</blockquote>",
      parse_mode="html",
      reply_markup=kb.cancel_keyboard
   )
   await callback.answer()


@router.callback_query(F.data.startswith("appost_"))
async def cb_approve_post(callback : CallbackQuery):
   print(callback.data)
   hashtags = callback.data.split("|")[1]
   user_id = int(callback.data.replace("appost_", "").replace(f"|{hashtags}", ""))
   print(user_id)

   user_chat = await bot.get_chat(user_id)
   me = await bot.get_me()

   await req.add_stars_for_post(user_id)
   await req.add_published_posts(me.id)

   js.add_hw_count(
      "all_time",
      user_chat.first_name,
      user_id,
      user_chat.username,
      1
   )
   js.add_hw_count(
      "this_year",
      user_chat.first_name,
      user_id,
      user_chat.username,
      1
   )

   await callback.message.edit_reply_markup(reply_markup=kb.approve_post_keyboard)

   await bot.send_message(
      chat_id=user_id,
      text=f"<b>✅ Ваши ответы одобрены</b>\n\n"
           f"<blockquote>{decode(hashtags)}</blockquote>\n\n"
           f"+{con.post_price} ⭐️",
      parse_mode="html",
      reply_markup=kb.open_profile_keyboard
   )
   await callback.answer()


# Это чеккер той самой кнопки, которая просто обозначает, что пост был одобрен
@router.callback_query(F.data == "dont_checked_this")
async def cb_dont_checked(callback : CallbackQuery):
   await callback.answer("Пост был одобрен", show_alert=True)


@router.callback_query(F.data.startswith("decline_post_"))
async def cb_decline_post(callback : CallbackQuery, state : FSMContext):
   tags = callback.data.split("|")[1]
   user_id = int(callback.data.replace("decline_post_", "").replace(f"|{tags}", ""))
   
   await state.set_state(Decline_Post.hashtags)
   await state.update_data(hashtags=tags)
   await state.set_state(Decline_Post.user_id)
   await state.update_data(user_id=user_id)
   await state.set_state(Decline_Post.reason)

   await callback.message.answer("<b>📝 Причина отклонения:</b>", parse_mode="html")
   await callback.answer()


@router.message(Decline_Post.reason)
async def msg_decline_reason(message : Message, state : FSMContext):
   data = await state.get_data()
   user_id = data.get("user_id")
   hashtags = data.get("hashtags")

   await bot.send_message(
      chat_id=user_id,
      text=f"<b>💢 Ответы не одобрены</b>\n\n"
           f"<blockquote>{decode(hashtags)}</blockquote>\n\n"
           f"<blockquote><b>Причина:</b>\n{message.text}</blockquote>",
      parse_mode="html"
   )

   await message.answer("✅ Сообщение отправлено")
   await state.clear()


@router.callback_query(F.data.startswith("ask_question_"))
async def cb_ask_question(callback : CallbackQuery, state : FSMContext):
   user_id = int(callback.data.replace("ask_question_", ""))
   
   await state.set_state(Ask_question.user_id)
   await state.update_data(user_id=user_id)
   await state.set_state(Ask_question.reason)

   await callback.message.answer("<b>📝 Ваш вопрос:</b>", parse_mode="html")
   await callback.answer()


@router.message(Ask_question.reason)
async def msg_question(message : Message, state : FSMContext):
   data = await state.get_data()
   user_id = data.get("user_id")

   await bot.send_message(
      chat_id=user_id,
      text=f"<b>🛎 Новый вопрос</b>\n\n"
           f"<blockquote>{message.text}</blockquote>",
      reply_markup=kb.answer_keyboard,
      parse_mode="html"
   )

   await message.answer("✅ Сообщение отправлено")
   await state.clear()


@router.callback_query(F.data == "answer")
async def cb_answer(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Answer.answer)

   await callback.message.answer(
      "📝 Ваш ответ:"
   )

   await callback.answer()


@router.message(Answer.answer)
async def msg_answer(message : Message, state : FSMContext):
   await state.clear()

   await bot.send_message(
      chat_id=con.reports_chat_id,
      message_thread_id=con.offers,
      text=f"<b>Новый ответ от {message.from_user.full_name}</b>\n\n"
           f"<blockquote>{message.text}</blockquote>",
      parse_mode="html",
      reply_markup=await kb.ask_question_keyboard(message.from_user.id)
   )


@router.callback_query(F.data.startswith("close_dialog_"))
async def cb_close_dialog(callback : CallbackQuery, state : FSMContext):
   user_id = int(callback.data.replace("close_dialog_", ""))
   await state.clear()

   await callback.message.answer("🤝 Диалог успешно закрыт")
   await bot.send_message(
      chat_id=user_id,
      text="🤝 Диалог успешно окончен"
   )
   await callback.answer("Диалог закрыт")


@router.callback_query(F.data == "check_subscribe")
async def cb_check_subscribe(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Homework.grade)
   
   # Проверка на то, есть ли пользователь ХОТЯ БЫ в одном канале
   is_subscribe = bool(
      True in [await user_sub_check(callback.from_user.id, i) for i in con.channels_id_for_subscribe]
   )
   
   if not is_subscribe:
      await callback.answer("❌ Вы не подписались ни на один канал! ", show_alert=True)
   else:
      await callback.message.delete()
      await callback.message.answer(
         "<b>🎓 Выберите класс</b>",
         parse_mode="html",
         reply_markup=await kb.grades_keyboard_builder("search")
      )
   
   await callback.answer("Спасибо ❤️")


@router.callback_query(F.data == "formatting_post")
async def cb_formatting_post(callback : CallbackQuery, state : FSMContext):
   await state.set_state(Post.format_post)
   await callback.message.answer("📩 Перешлите пост, который нужно форматировать:")
   await callback.answer()


@router.message(Post.format_post)
async def msg_post_for_formatting(message : Message, state : FSMContext):
   
   # принимаем ответы

   await message.answer(
      text="🕹 Опции",
      reply_markup=kb.option_post_keyboard
   )

   await state.clear()


@router.callback_query(F.data == "done_formatting_post")
async def cb_done_formatting_post(callback : CallbackQuery, state : FSMContext):
   await state.clear()
   
   await callback.message.edit_text(
      "✅ Пост отформатирован"
   )

   await callback.answer()


@router.callback_query(F.data == "get_money")
async def cb_get_money(callback : CallbackQuery, state : FSMContext):
   await state.clear()
   user = await req.get_user(callback.from_user.id)
   
   if user.stars > 0:
      await callback.message.edit_text(
         f"👇 <b>Выберите, что хотите получить</b>",
         parse_mode="html",
         reply_markup=await kb.what_getting_keyboard_builder(user.stars)
      )
      await callback.answer()
   else:
      await callback.answer(f"У вас недостаточно средств", show_alert=True)


@router.callback_query(F.data.startswith("get_rub_"))
async def cb_get_rubs(callback : CallbackQuery, state : FSMContext):
   rubs = int(callback.data.replace("get_rub_", ""))

   await state.set_state(User_card.card_link)
   await callback.message.edit_text(
      f"👇 <b>Отправьте свои реквизиты</b>\n\n"
      f"В течении дня вам поступят {rubs}₽",
      parse_mode="html",
      reply_markup=kb.back_to_what_getting_keyboard
   )
   await callback.answer()


@router.message(User_card.card_link)
async def msg_card_link(message : Message, state : FSMContext):
   await state.clear() # Очищаем, пушто не нужно ничего записывать

   user = await req.get_user(message.from_user.id)

   await bot.send_message(
      chat_id=con.reports_chat_id,
      text=
      f"<b>Запрос на вывод</b>\n"
      f"{user.stars*2}₽\n\n"
      f"<b>Реквизиты:</b>\n"
      f"<span class='tg-spoiler'>{message.text}</span>\n\n"
      f"<b>ID пользователя:</b>\n"
      f"<pre>{message.from_user.id}</pre>",
      parse_mode="html",
      message_thread_id=con.debit_money
   )
   await message.answer("👌 Ожидайте оплату")


@router.callback_query(F.data.startswith("get_stars_"))
async def cb_get_stars(callback : CallbackQuery):
   user = await req.get_user(callback.from_user.id)

   await bot.send_message(
      chat_id=con.reports_chat_id,
      text=
      f"<b>Запрос на вывод</b>\n"
      f"{user.stars} stars\n\n"
      f"<b>Реквизиты:</b>\n"
      f"<span class='tg-spoiler'>@{callback.from_user.username}</span>\n\n"
      f"<b>ID пользователя:</b>\n"
      f"<pre>{callback.from_user.id}</pre>\n\n"
      f"<b>Доп. ссылка:</b>\n"
      f"tg://user?id={callback.from_user.id}",
      parse_mode="html",
      message_thread_id=con.debit_money
   )
   await callback.message.edit_text("👌 Ожидайте оплату")


@router.callback_query(F.data == "back_to_profile")
async def cb_cancel_money(callback : CallbackQuery, state : FSMContext):
   user = await req.get_user(callback.from_user.id)

   await state.clear()
   await callback.message.edit_text(
      f"🎅 <b>Это ваш профиль</b>\n"
      f"ID: {callback.from_user.id}\n\n"
      f"<b>Статистика:</b>\n"
      f"Ваши ДЗ: {user.posts}\n\n"
      f"<b>Баланс:</b>\n"
      f"⭐️ {user.stars} ≈ {user.stars*2}₽",
      parse_mode="html",
      reply_markup=kb.profile_keyboard
   )
   await callback.answer()


"""@router.callback_query(F.data == "clear_user_money")
async def cb_clear_money(callback : CallbackQuery):
   await callback.message.answer(
      "‼️ Вы уверены, что хотите списать деньги?",
      reply_markup=kb.are_you_sure
   )


@router.callback_query(F.data == "im_sure")
async def cb_im_sure(callback : CallbackQuery):
   await req.clear_stars()
   await callback.message.answer(
      "✅ Деньги списаны"
   )"""


# --------------------------------------------------
# ДРУГИЕ ФУНКЦИИ
# --------------------------------------------------


async def mail_results():
   top_list = "\n".join(js.get_users_names("this_year", 3))

   if top_list == "":
      top_list = "Список пуст..."
   
   await mailing(
      f"<b>Поздравляем с окончанием учебного года!! ❤️</b>\n\n"
      f"<b>🏆 Победители:</b>\n"
      f"{top_list}"
   )

   # А тут мы должны кидать сообщение всем 3-м победителям
   winner_list = js.get_winners()

   for winner in winner_list:
      await req.add_stars(winner[1], int(winner[4]/2))
      try:
         await bot.send_message(
            chat_id=winner[1],
            text=f"<b><a href='https://t.me/{winner[2]}'>{winner[0]}</a>, ты занял {winner[3]}-е место в топе 🎉</b>\n\n"
                 f"<b>🎁 {winner[4]}₽</b>\n\n",
            parse_mode="html",
            reply_markup=kb.open_profile_keyboard,
            message_effect_id="5046509860389126442",
            disable_web_page_preview=True
         )
      except Exception as e:
         print(f"error: {e}")


@router.message(Command("mail"))
async def msg_mail(message : Message, command : CommandObject, state : FSMContext):
   await state.clear()
   if message.from_user.id == con.owner_id:
      text = command.args
      await mailing(text)


# Создаем пост (с помощью билдера), используя данные из состояния
async def create_post(data):
   teacher_comment, user_comment = data["teacher_comment"], data["user_comment"]
   album_messages = data["answers"]
   builder = MediaGroupBuilder()
   
   text = [
      f"{data['hashtags']}\n",
      f"<b>Оценка {data['rating']}</b>",
      f"<b>{data['by_user']}</b>\n" if data['by_user'] != "" else "",
   ]

   # Если коммент учителя есть, то добавляем его
   if teacher_comment and teacher_comment not in "":
      text.append(f"<blockquote><b>Комментарий учителя:</b>")
      text.append(f"{data['teacher_comment']}</blockquote>\n")

   # Если есть коммент юзера, то добавляем
   if user_comment and user_comment not in "":
      text.append(f"{data['user_comment']}")

   text = [i for i in text if i != ""] # Убираем пустые строки
   text = "\n".join(text)

   for i, msg in enumerate(album_messages):
      builder.add(
         type=get_media_type(msg),
         media=get_media_file_id(msg),
         caption=text if i == 0 else None,
         parse_mode="html" if i == 0 else None
      )

   post = builder.build()
   return post


# Тут тоже создаем пост (и сразу отправляем), но уже для одного медиа
async def answer_one_media_post(data, message : Message, chat_id : Optional[int] = None):
   teacher_comment, user_comment = data["teacher_comment"], data["user_comment"]
   media_type = get_media_type(message)
   media_file = get_media_file_id(message)

   text = [
      f"{data['hashtags']}\n",
      f"<b>Оценка {data['rating']}</b>",
      f"<b>{data['by_user']}</b>\n" if data['by_user'] != "" else "",
   ]

   # Если коммент учителя есть, то добавляем его
   if teacher_comment and teacher_comment not in "":
      text.append(f"<blockquote><b>Комментарий учителя:</b>")
      text.append(f"{data['teacher_comment']}</blockquote>\n")

   # Если есть коммент юзера, то добавляем
   if user_comment and user_comment not in "":
      text.append(f"{data['user_comment']}")

   text = [i for i in text if i != ""] # Убираем пустые строки
   text = "\n".join(text)

   if chat_id: # Если указываем id чата, то кидаем пост другим способом
      if media_type == "photo":
         await bot.send_photo(
            chat_id=chat_id,
            message_thread_id=con.offers,
            photo=media_file,
            caption=text,
            parse_mode="html"
         )

      elif media_type == "video":
         await bot.send_video(
            chat_id=chat_id,
            message_thread_id=con.offers,
            video=media_file,
            caption=text,
            parse_mode="html"
         )

      elif media_type == "document":
         await bot.send_document(
            chat_id=chat_id,
            message_thread_id=con.offers,
            document=media_file,
            caption=text,
            parse_mode="html"
         )

   else: # Если id'шника нету, то кидаем пользователю в лс
      if media_type == "photo":
         await message.answer_photo(media_file, caption=text, parse_mode="html")
      elif media_type == "video":
         await message.answer_video(media_file, caption=text, parse_mode="html")
      elif media_type == "document":
         await message.answer_document(media_file, caption=text, parse_mode="html")