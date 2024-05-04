import telebot
import sqlite3
import logging
from config import TOKEN
import symbols
import messages
from datetime import date

bot = telebot.TeleBot(TOKEN, parse_mode="markdown")
logger = telebot.logger

def calc_spendings_sum(data):
    spendings = sum([s for t in data for s in t])
    return spendings

def get_args(msg):
    return msg.text.split()[1:]

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, messages.GREETING)

@bot.message_handler(commands=["add"])
def add(message):
    conn = sqlite3.connect("./db.sqlite3")
    cursor = conn.cursor()

    query = "select id from categories"
    cursor.execute(query)
    categories_ids = [i for t in cursor.fetchall() for i in t]

    query = "select name from categories"
    cursor.execute(query)
    categories_names = [n for t in cursor.fetchall() for n in t]
    categories_names_short = [
            n[0] + n.split()[1][0] if len(n.split()) > 1 else n[0]
            for n in categories_names
            ]
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
            query = f"insert into spendings (amount, category_id) values \
                    ({spending_amount}, {category_id})"
            cursor.execute(query)
            bot.send_message(message.chat.id,
                             f"{symbols.SUCCESS} трата на *{category_name}* успешно добавлена")
        else:
            bot.send_message(message.chat.id,
                             f"{symbols.WARNING} категория не найдена")
    else:
        query = f"insert into spendings (amount) values ({spending_amount});"
        cursor.execute(query)
        bot.send_message(message.chat.id,
                         f"{symbols.SUCCESS} трата успешно добавлена")

    cursor.close()
    conn.commit()

@bot.message_handler(commands=["stats"])
def stats(message):
    today_date = date.today()

    conn = sqlite3.connect("./db.sqlite3")
    cursor = conn.cursor()

    query = "select amount from spendings"
    cursor.execute(query)
    total_data = cursor.fetchall()
    total_spendings = calc_spendings_sum(total_data)

    query = "select amount from spendings where date(spending_date) = ?"
    cursor.execute(query, (today_date,))
    today_data = cursor.fetchall()
    today_spendings = calc_spendings_sum(today_data)

    cursor.execute("select name from categories")
    categories = [c for t in cursor.fetchall() for c in t]
    spendings_by_category = dict()
    for c in categories:
        query = f"select amount from spendings join categories \
                on category_id = categories.id where name = '{c}'"
        cursor.execute(query)
        total = sum(int(s) for t in cursor.fetchall() for s in t)
        spendings_by_category |= {f"{c}": total}

    bot.send_message(message.chat.id,
                     messages.get_stats(today_spendings, total_spendings, **spendings_by_category),
                     parse_mode="Markdown")

@bot.message_handler(commands=["clear"])
def clear(message):
    conn = sqlite3.connect("./db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("delete from spendings")
    cursor.close()
    conn.commit()

if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    bot.infinity_polling()
