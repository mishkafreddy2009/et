import symbols
import messages

from datetime import date, datetime
import os
import sys
import logging

import telebot
import sqlite3 as sl


TOKEN = os.getenv("ET_TOKEN")
DB_FILE = "./et.db"

if not TOKEN:
    print("[err] token not found")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode="markdown")
logger = telebot.logger

def create_db(db_file):
    con = sl.connect(db_file)
    c = con.cursor()
    c.execute("""
              create table users (
                id integer primary key autoincrement,
                telegram_id integer unique not null
              )
              """)
    c.execute("""
              create table categories (
                id integer primary key autoincrement,
                name text not null,
                name_short text,
                user_id integer not null,
                foreign key (user_id) references users (id)
              )
              """)
    c.execute("""
              create table spendings (
                id integer primary key autoincrement,
                amount integer not null,
                datetime text not null,
                category_id integer,
                user_id integer not null,
                foreign key (category_id) references categories (id),
                foreign key (user_id) references users (id)
              )
              """)
    con.commit()
    con.close()

def check_db_status(db_file):
    con = sl.connect(db_file)
    c = con.cursor()
    data = c.execute("select count(*) from sqlite_master")
    c.close()
    for row in data:
        if row[0] == 0:
            create_db(db_file)

def get_first_letters(word: str) -> str:
    return word[0] + word.split()[1][0] if len(word.split()) > 1 else word[0]

def get_raw_data(data) -> list:
    return [item for tup in data for item in tup]

def calculate_sum(data) -> int:
    return sum([s for t in data for s in t])

def get_args(message) -> list:
    return message.text.split()[1:]

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    con = sl.connect(DB_FILE)
    c = con.cursor()
    c.execute("select id from users where telegram_id = ?", (user_id,))
    user_data = c.fetchone()
    if not user_data:
        c.execute("insert into users (telegram_id) values (?)", (user_id,))
        con.commit()
        con.close()
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.add(telebot.types.KeyboardButton("добавить трату"))
    keyboard.add(telebot.types.KeyboardButton("добавить категорию"))
    keyboard.add(telebot.types.KeyboardButton("посмотреть доступные категории"))
    bot.send_message(message.chat.id, messages.GREETING, reply_markup=keyboard)

@bot.message_handler(commands=["add"])
def add(message):
    user_id = message.from_user.id
    con = sl.connect(DB_FILE)
    c = con.cursor()

    args = get_args(message)

    if not args:
        bot.send_message(message.chat.id, f"{symbols.WARNING} введите сумму траты")
        return
    try:
        amount = int(args[0])
    except:
        bot.send_message(message.chat.id, f"{symbols.WARNING} сумма траты должна быть числом")
        return

    c.execute("select name, name_short, id from categories where user_id = ?", (user_id,))
    categories = c.fetchall()

    if len(args) > 1:
        category_name = "".join(arg for arg in args[1:])
        for i in range(len(categories)):
            category_names = categories[i][:2]
            if category_name in category_names:
                category_id = categories[i][2]
                category_fullname = category_names[0]
                c.execute("""
                          insert into spendings (amount, category_id, user_id, datetime)
                          values (?, ?, ?, ?)
                          """,
                          (amount, category_id, user_id, datetime.now()))
                con.commit()
                c.close()
                bot.send_message(message.chat.id,
                                 f"{symbols.SUCCESS} трата в размере *{amount} руб* на *{category_fullname}* успешно добавлена")
                return

    c.execute("""
              insert into spendings (amount, user_id, datetime)
              values (?, ?, ?)
              """,
              (amount, user_id, datetime.now()))
    con.commit()
    c.close()
    bot.send_message(message.chat.id,
                     f"{symbols.SUCCESS} трата в размере *{amount} руб* успешно добавлена")

@bot.message_handler(commands=["stats", "stat"])
def stats(message):
    user_id = message.from_user.id
    today_date = date.today()

    con = sl.connect(DB_FILE)
    c = con.cursor()

    c.execute("select amount from spendings where user_id = ?", (user_id,))
    data = c.fetchall()
    total_spendings = calculate_sum(data)

    c.execute("select amount from spendings where date(datetime) = ? and user_id = ?", (today_date, user_id))
    print(today_date)
    data = c.fetchall()
    today_spendings = calculate_sum(data)

    c.execute("select c.name, sum(s.amount) from spendings s join categories c on s.category_id = c.id where s.user_id = ? group by name", (user_id,))
    data = c.fetchall()
    categories_spendings = {name: total for name, total in data}
    bot.send_message(message.chat.id,
                     messages.get_stats(today_spendings, total_spendings, **categories_spendings))

@bot.message_handler(commands=["addcategory"])
def add_category(message):
    user_id = message.from_user.id
    con = sl.connect(DB_FILE)
    c = con.cursor()

    args = get_args(message)

    if len(args) == 0:
        bot.send_message(message.chat.id, f"{symbols.WARNING} укажите название категории")
        return

    category = " ".join(arg for arg in args)
    category_short = get_first_letters(category)

    c.execute("select name from categories where user_id = ?", (user_id,))
    user_categories = get_raw_data(c.fetchall())

    if len(user_categories) > 10:
        bot.send_message(message.chat.id, f"{symbols.WARNING} нельзя добавить более 10 категорий")
        return
    if category in user_categories:
        bot.send_message(message.chat.id, f"{symbols.WARNING} категория уже добавлена")
        return

    c.execute("insert into categories (name, name_short, user_id) values (?, ?, ?)", (category, category_short, user_id,))
    bot.send_message(message.chat.id, f"{symbols.SUCCESS} категория *{category}* добавлена")
    con.commit()
    c.close()

@bot.message_handler(commands=["categories"])
def categories(message):
    user_id = message.from_user.id
    con = sl.connect(DB_FILE)
    c = con.cursor()
    c.execute("select name, name_short from categories where user_id = ?", (user_id,))
    data = c.fetchall()
    c.close()
    categories = {name: name_short for name, name_short in data}
    bot.send_message(message.chat.id,
                     messages.get_categories(categories))

@bot.message_handler(commands=["clear"])
def clear(message):
    con = sl.connect("./db.sqlite3")
    c = con.cursor()
    c.execute("delete from spendings")
    c.close()
    con.commit()
    bot.send_message(message.chat.id,
                     f"{symbols.SUCCESS} удалено")

if __name__ == "__main__":
    check_db_status(DB_FILE)
    # logger.setLevel(logging.DEBUG)
    bot.infinity_polling()
