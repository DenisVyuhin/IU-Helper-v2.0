import json
import constants as con


def get_users(path: str = "all_time", amount: int = 15) -> list:
   users = []

   with open("stats.json", "r", encoding="utf-8") as file:
      data = json.load(file)

   for user in data[path]:
      users.append(f'{user["name"]} — <b>{user["hw_count"]} ДЗ</b>')

   # Сортируем пользователей по количеству ДЗ (по убыванию)
   users = sorted(
      users,
      key=lambda x: int(x.split("—")[1].replace(" ", "").replace("ДЗ</b>", "").replace("<b>", "")),
      reverse=True
   )

   # Ограничиваем количество ОТОБРАЖАЕМЫХ пользователей в списке
   if amount > len(users):
      this_amount = len(users)
   elif amount <= len(users):
      this_amount = amount

   # Формируем список с пользователями для отображения + добавляем нумерацию (по убыванию)
   result_list = [
      f"{i+1}. {users[i]}" for i in range(this_amount)
   ]

   return result_list


# Тот же самый вывод людей, НО только имен
# То есть вместо этого "Денчик - 12 ДЗ" будет это "Денчик"
def get_users_names(path: str = "all_time", amount: int = 15) -> list:
   users = []

   with open("stats.json", "r", encoding="utf-8") as file:
      data = json.load(file)

   for user in data[path]:
      users.append(f'{user["name"]}|{user["user_name"]} — {user["hw_count"]}') # Тут будет с кол-во ДЗ, чтобы потом отсортировать

   # Сортируем
   users = sorted(
      users,
      key=lambda x: int(x.split("—")[1].replace(" ", "")),
      reverse=True
   )

   if amount > len(users):
      this_amount = len(users)
   elif amount <= len(users):
      this_amount = amount

   # А уже тут мы все обрезаем и оставляем только имя (ТАКЖЕ ДОБАВИТЬ СУММУ ВЫИГРЫША)
   result_list = [
      f'{i+1}. <a href="https://t.me/{users[i].split("—")[0].split("|")[1].split()[0]}">{users[i].split("—")[0].split("|")[0]}</a> — <b>{con.winner_price[i]}₽</b>'
      for i in range(this_amount)
   ]

   return result_list


# Вывод победителей, НО уже их id'шников
def get_winners_elements(path: str = "all_time") -> list:
   users = []
   amount_winners = 3

   with open("stats.json", "r", encoding="utf-8") as file:
      data = json.load(file)

   for user in data[path]:
      users.append(f'{user["name"]}|{user["user_id"]}|{user["user_name"]}—{user["hw_count"]}') # Тут будет с кол-во ДЗ, чтобы потом отсортировать

   # Сортируем
   users = sorted(
      users,
      key=lambda x: int(x.split("—")[1].replace(" ", "")),
      reverse=True
   )

   if amount_winners > len(users):
      this_amount = len(users)
   elif amount_winners <= len(users):
      this_amount = amount_winners

   # В итоге будет 'Денчик|12345789|KodersUp|1' (имя|id|юз|место)
   result_list = [
      f'{users[i].split("—")[0]}|{i+1}'
      for i in range(this_amount)
   ]

   return result_list

# Вывод списка победителей [Имя, id, юз, место, сумма выигрыша]
def get_winners() -> list:
   winners = []
   win_list = get_winners_elements("this_year")

   for i in range(0, len(win_list)):
      element = win_list[i].split("|")
      winners.append(
         [
            element[0],         # Имя
            int(element[1]),    # id челика
            str(element[2]),    # Юзернейм
            int(element[3]),    # Место
            con.winner_price[i] # Сумма выигрыша
         ]
      )

   return winners


def add_hw_count(path: str = "", name: str = "", user_id: int = 0, user_name: str = "None", count: int = 0) -> None:
   with open("stats.json", "r", encoding="utf-8") as file:
      data = json.load(file)
   
   is_user = False

   for user in data[path]:
      if user["user_id"] == user_id:
         user["hw_count"] += count
         user["user_name"] = user_name # На всякий случай обновляем юзернейм
         is_user = True
         break
   
   if not is_user:
      data[path].append({
         "name": name,
         "user_id": user_id,
         "user_name": user_name,
         "hw_count": count
      })
   
   with open("stats.json", "w", encoding="utf-8") as file:
      json.dump(data, file, indent=3, ensure_ascii=False)


def clear_hw_count(path: str = "") -> None:
   with open("stats.json", "w", encoding="utf-8") as file:
      data = json.load(file)

      for user in data[path]:
         user["hw_count"] = 0
      json.dump(data, file, indent=3, ensure_ascii=False)


# --------------------------------------------------
# БАН/РАЗБАН ПОЛЬЗОВАТЕЛЯ
# --------------------------------------------------


def ban_user(user_id: int) -> None:
   with open("banned.json", "r", encoding="utf-8") as file:
      data = json.load(file)

   if "banned" not in data:
      data["banned"] = []

   if user_id not in data["banned"]:
      data["banned"].append(user_id)

   with open("banned.json", "w", encoding="utf-8") as file:
      json.dump(data, file, indent=3, ensure_ascii=False)


def unban_user(user_id: int) -> None:
   with open("banned.json", "r", encoding="utf-8") as file:
      data = json.load(file)

   if "banned" not in data:
      data["banned"] = []

   if user_id in data["banned"]:
      data["banned"].remove(user_id)

   with open("banned.json", "w", encoding="utf-8") as file:
      json.dump(data, file, indent=3, ensure_ascii=False)


def get_banned_users() -> list:
   with open("banned.json", "r", encoding="utf-8") as file:
      data = json.load(file)

   if "banned" not in data:
      data["banned"] = []

   return data["banned"]