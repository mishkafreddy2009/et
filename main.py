import telebot
import sqlite3
import logging
from config import TOKEN
import symbols
import messages
from datetime import date


bot = telebot.TeleBot(TOKEN, parse_mode="markdown")
logger = telebot.logger

def get_first_letters(words: list[str]):
    return [s[0] + s.split()[1][0] if len(s.split()) > 1 else s[0] for s in words]

def get_raw_data(data):
    return [item for tup in data for item in tup]

def calculate_sum(data):
    return sum([s for t in data for s in t])

def get_args(msg):
    return msg.text.split()[1:]

@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.send_message(message.chat.id, messages.GREETING)

@bot.message_handler(commands=["add"])
def add(message):
    conn = sqlite3.connect("./db.sqlite3")
    c = conn.cursor()

    c.execute("select id from categories")
    data = c.fetchall()
    categories_ids = get_raw_data(data)

    c.execute("select name from categories")
    data = c.fetchall()
    categories_names = get_raw_data(data)
    categories_names_short = get_first_letters(categories_names)
    categories = {
            categories_names_short[i]: categories_ids[i]
            for i in range(len(categories_ids))
            }

    args = get_args(message)

    if not args:
        bot.send_message(message.chat.id,
                         f"{symbols.WARNING} введите сумму траты")
        return

    try:
        spending_amount = int(args[0])
    except:
        bot.send_message(message.chat.id,
                         f"{symbols.WARNING} сумма траты должна быть числом")
        return

    if len(args) > 1:
        category = args[1]
        category_id = categories.get(category)
        if category_id:
            category_name = categories_names[category_id-1]
            c.execute(f"insert into spendings (amount, category_id) values \
                    ({spending_amount}, {category_id})")
            bot.send_message(message.chat.id,
                             f"{symbols.SUCCESS} трата на *{category_name}* успешно добавлена")
        else:
            bot.send_message(message.chat.id,
                             f"{symbols.WARNING} категория не найдена")
    else:
        c.execute("insert into spendings (amount) values ({spending_amount})")
        bot.send_message(message.chat.id,
                         f"{symbols.SUCCESS} трата успешно добавлена")

    c.close()
    conn.commit()

@bot.message_handler(commands=["stats", "stat"])
def stats(message):
    today_date = date.today()

    conn = sqlite3.connect("./db.sqlite3")
    c = conn.cursor()

    query = "select amount from spendings"
    c.execute(query)
    total_data = c.fetchall()
    total_spendings = calculate_sum(total_data)

    query = "select amount from spendings where date(spending_date) = ?"
    c.execute(query, (today_date,))
    today_data = c.fetchall()
    today_spendings = calculate_sum(today_data)

    c.execute("select name from categories")
    data = c.fetchall()
    categories = get_raw_data(data)
    spendings_by_category = dict()
    for category in categories:
        c.execute(f"select amount from spendings join categories \
                on category_id = categories.id where name = '{category}'")
        data = c.fetchall()
        # total = sum(int(s) for t in data for s in t)
        total = calculate_sum(data)
        spendings_by_category |= {f"{category}": total}

    bot.send_message(message.chat.id,
                     messages.get_stats(today_spendings, total_spendings,
                                        **spendings_by_category),)

@bot.message_handler(commands=["categories"])
def categories(message):
    conn = sqlite3.connect("./db.sqlite3")
    c = conn.cursor()
    c.execute("select name from categories")
    data = c.fetchall()
    c.close()
    categories_long = get_raw_data(data)
    categories_short = get_first_letters(categories_long)
    categories = {categories_long[i]: categories_short[i] for i in range(len(categories_long))}
    bot.send_message(message.chat.id,
                     messages.get_categories(categories))

@bot.message_handler(commands=["clear"])
def clear(message):
    conn = sqlite3.connect("./db.sqlite3")
    c = conn.cursor()
    c.execute("delete from spendings")
    c.close()
    conn.commit()
    bot.send_message(message.chat.id,
                     f"{symbols.SUCCESS} удалено")

if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    bot.infinity_polling()
