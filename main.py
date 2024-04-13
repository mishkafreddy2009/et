import sqlite3
import telebot
import logging

import messages
import symbols
from config import TOKEN, SQLITE_DB_FILE


bot = telebot.TeleBot(TOKEN, parse_mode=None)
logger = telebot.logger


def get_args(msg):
    return msg.text.split()[1:]


@bot.message_handler(commands=["start"])
def send_welcome(msg):
    bot.send_message(msg.chat.id, messages.GREETING)


@bot.message_handler(commands=["add"])
def add_spending(msg):
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cursor = conn.cursor()

    args = get_args(msg)

    if not args:
        bot.send_message(msg.chat.id, f"{symbols.WARNING} введите сумму траты")
        return

    try:
        spending_amount = int(args[0])
    except:
        bot.send_message(msg.chat.id,
                         f"{symbols.WARNING} сумма траты должна быть числом")
        return

    cursor.execute(f"insert into spending (amount) values ({spending_amount});")

    bot.send_message(msg.chat.id, f"{symbols.SUCCESS} трата успешно добавлена")

    cursor.close()

    conn.commit()


@bot.message_handler(commands=["stats"])
def send_stats(msg):
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cursor = conn.cursor()

    cursor.execute("select amount from spending;")
    all_data = cursor.fetchall()
    cursor.close()
    total_spending = sum([amount for amounts in all_data for amount in amounts])
    bot.send_message(msg.chat.id,
                     symbols.INFO + messages.get_stats(total_spending),
                     parse_mode="Markdown")


@bot.message_handler(commands=["devdel"])
def remove(msg):
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("delete from spending;")
    cursor.close()
    conn.commit()


if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    bot.infinity_polling()
