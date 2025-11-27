from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from constants import grades, school_subject, quarters, weeks, years

import app.handlers as hnd


start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="👤 Мой профиль", callback_data="open_profile")],
   [InlineKeyboardButton(text="🔎 Найти ДЗ", callback_data="search_dz"), InlineKeyboardButton(text="💡 Предложить ДЗ", callback_data="offer_dz")],
   # [InlineKeyboardButton(text="📚 Купить ДЗ", callback_data="buy_dz")],
   [InlineKeyboardButton(text="🏆 ТОП", callback_data="stats")]
])


search_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="🔎 Найти еще", callback_data="search_dz")]
])


try_search_again_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="search_dz")]
])


subscribe_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscribe")]
])


profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Вывести деньги", callback_data="get_money")],
   [InlineKeyboardButton(text="Закрыть", callback_data="cancel")]
])


theme_question_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="О боте", callback_data="question_about_bot")],
   [InlineKeyboardButton(text="О InternetUrok", callback_data="question_about_iu")]
])


answers_about_bot_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Гарантии", callback_data="about_bot_faq_1")],
   [InlineKeyboardButton(text="Процесс заказа", callback_data="about_bot_faq_2")],
   [InlineKeyboardButton(text="Все комманды", callback_data="about_bot_faq_3")],
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_theme_question")]
])


answers_about_iu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Минимум ДЗ", callback_data="about_iu_faq_1")],
   [InlineKeyboardButton(text="Баллы и оценки", callback_data="about_iu_faq_2")],
   [InlineKeyboardButton(text="ДЗ от руки/электронно", callback_data="about_iu_faq_3")],
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_theme_question")]
])


back_to_bot_answers_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_bot_questions")]
])


back_to_iu_answers_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_iu_questions")]
])


async def what_getting_keyboard_builder(amount_stars: int):
   keyboard = InlineKeyboardBuilder()

   rubs = amount_stars*2
   strs = amount_stars

   keyboard.add(InlineKeyboardButton(text=f"{rubs} рублей", callback_data=f"get_rub_{rubs}"))
   keyboard.add(InlineKeyboardButton(text=f"{strs} звезд", callback_data=f"get_stars_{strs}"))
   keyboard.add(InlineKeyboardButton(text=f"‹ Назад", callback_data=f"back_to_profile"))
   keyboard.adjust(1)

   return keyboard.as_markup()


back_to_what_getting_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="‹ Назад", callback_data="get_money")]
])


get_money_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_profile")]
])


async def post_keyboard_builder(user_id: int, hashtags: str) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()

   # Approve post -> appost
   keyboard.add(InlineKeyboardButton(text="✅ Одобрить", callback_data=f"appost_{user_id}|{hnd.code(hashtags)}"))
   keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_post_{user_id}|{hnd.code(hashtags)}"))
   keyboard.add(InlineKeyboardButton(text="❓ Задать вопрос", callback_data=f"ask_question_{user_id}"))
   #keyboard.add(InlineKeyboardButton(text="🤖 Форматировать (ИИ)", callback_data=f"formatting_post"))
   keyboard.adjust(1)
   
   return keyboard.as_markup()


# Клавиатура с опциями для поста (появляется после того, как ИИ отформатируем текст поста)
option_post_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="🔄 Повторить форматирование", callback_data="formatting_post")],
   [InlineKeyboardButton(text="Готово", callback_data="done_formatting_post")],
])


# Клавиатура для того, чтобы пользователь мог ответить на вопрос на счет поста
answer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Ответить", callback_data="answer")],
])


# Клавиатура для того, чтобы АДМИН мог задать новый вопрос ИЛИ закрыть диалог
async def ask_question_keyboard(user_id: int) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   keyboard.add(InlineKeyboardButton(text="Ответить", callback_data=f"ask_question_{user_id}"))
   keyboard.add(InlineKeyboardButton(text="Закрыть диалог", callback_data=f"close_dialog_{user_id}"))
   keyboard.adjust(1)
   
   return keyboard.as_markup()


# Эта клава лишь для того, чтобы обозначить, что пост был одобрен
# У нее больше нет функционала и какие-либо действия она не выполняет
approve_post_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="✅ Пост был одобрен", callback_data="dont_checked_this")],
])


# Клавиатура для того, чтобы ответить пользователю
async def operator_answer_keyboard_builder(user_id : int) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   keyboard.add(InlineKeyboardButton(text="Ответить", callback_data=f"operator_answer_{user_id}"))
   keyboard.add(InlineKeyboardButton(text="Завершить", callback_data=f"close_chat_{user_id}"))
   keyboard.adjust(1)

   return keyboard.as_markup()


# Клавиатура с оценками
async def rating_keyboard_builder() -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   for i in range(2, 6):
      keyboard.add(InlineKeyboardButton(text=f"{i}", callback_data=f"rating_{i}"))
   keyboard.adjust(4)
   
   return keyboard.as_markup()


skip_teacher_comment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Пропустить ›", callback_data="skip_teacher_comment")]
])


skip_user_comment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Пропустить ›", callback_data="skip_user_comment")]
])


edit_post_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_post")],
   [InlineKeyboardButton(text="✅ Завершить создание", callback_data="ready_post")],
   [InlineKeyboardButton(text="🗑 Удалить пост", callback_data="remove_post")],
])


async def edit_options_keyboard_builder(hidden_user: bool = False):
   keyboard = InlineKeyboardBuilder()

   btn_text = "Добавить имя" if hidden_user else "Скрыть имя"

   keyboard.add(InlineKeyboardButton(text="Фото, видео или файлы", callback_data="edit_media"))
   keyboard.add(InlineKeyboardButton(text="Хештеги", callback_data="edit_hashtags"))
   keyboard.add(InlineKeyboardButton(text=btn_text, callback_data=f"edit_user_{hidden_user}"))
   keyboard.add(InlineKeyboardButton(text="Оценку", callback_data="edit_rating"))
   keyboard.add(InlineKeyboardButton(text="Комментарий учителя", callback_data="edit_teacher_comment"))
   keyboard.add(InlineKeyboardButton(text="Мой комментарий", callback_data="edit_user_comment"))
   keyboard.add(InlineKeyboardButton(text="‹ Назад", callback_data="back_to_edit_options"))
   keyboard.adjust(1)

   return keyboard.as_markup()


cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
])


open_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="📱 Открыть меню", callback_data="open_menu")]
])


buy_dz_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Купить ДЗ", callback_data="buy_dz")]
])


open_profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="👤 Открыть профиль", callback_data="open_profile")]
])


stats_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="За всё время", callback_data="top_all_time")],
   [InlineKeyboardButton(text="За учебный год", callback_data="top_this_quarter")],
])


back_to_stats_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_stats")]
])


"""clear_user_money = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Списать деньги пользователя", callback_data="clear_user_money")]
])


are_you_sure = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Да, уверен!", callback_data="im_sure")]
])"""


test_ready_order_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Изменить список", callback_data="✅ Готово")]
])


#! -------------------- ТИП ЗАКАЗА --------------------
order_type_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Отдельное ДЗ", callback_data=f"order_type_1")],
   [
      InlineKeyboardButton(text="Четверть", callback_data=f"order_type_2"),
      InlineKeyboardButton(text="Весь год", callback_data=f"order_type_3")
   ],
   [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
])


#! -------------------- КЛАССЫ --------------------
async def grades_keyboard_builder(event: str) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   for grade in grades:
      keyboard.add(InlineKeyboardButton(text=grade, callback_data=f"grade_{event}_{grade}"))
   keyboard.adjust(2)

   if event == "buy" or event == "buy_type_1":
      keyboard.add(InlineKeyboardButton(text="‹ Назад", callback_data=f"back_to_order_type"))
   
   return keyboard.as_markup()


back_to_select_grade_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="‹ Назад", callback_data="back_to_grades_buy_type_1")]
])


#! -------------------- ПРЕДМЕТЫ --------------------
async def subjects_keyboard_builder(event: str) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()

   for subject in school_subject:
      keyboard.add(InlineKeyboardButton(text=subject, callback_data=f"subject_{event}_{subject}"))
   
   keyboard.add(InlineKeyboardButton(text="‹ Назад", callback_data=f"back_to_grades_{event}"))
   keyboard.adjust(2)

   return keyboard.as_markup()


#! -------------------- ЧЕТВЕРТИ --------------------
async def quarters_keyboard_builder(event: str) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   for quar in quarters:
      keyboard.add(InlineKeyboardButton(text=quar, callback_data=f"quarter_{event}_{quar}"))
   
   keyboard.add(InlineKeyboardButton(text="‹ Назад", callback_data=f"back_to_subjects_{event}"))
   keyboard.adjust(1)
   
   return keyboard.as_markup()


#! -------------------- НЕДЕЛИ --------------------
async def weeks_keyboard_builder(quarter : int, event: str) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   for week in weeks[quarter-1]:
      keyboard.add(InlineKeyboardButton(text=week, callback_data=f"week_{event}_{week}"))
   
   keyboard.add(InlineKeyboardButton(text="‹ Назад", callback_data=f"back_to_quarters_{event}"))
   keyboard.adjust(2)
   
   return keyboard.as_markup()


#! -------------------- ГОДА --------------------
async def years_keyboard_builder(event: str) -> InlineKeyboardMarkup:
   keyboard = InlineKeyboardBuilder()
   
   for year in years:
      keyboard.add(InlineKeyboardButton(text=year, callback_data=f"year_{event}_{year}"))
   
   keyboard.add(InlineKeyboardButton(text="‹ Назад", callback_data=f"back_to_weeks_{event}"))
   keyboard.adjust(2)
   
   return keyboard.as_markup()