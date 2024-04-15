from sqlite3 import sqlite_version
import symbols
import messages
from datetime import date
from config import SQLITE_DB_FILE
from db_utils import connect_to_db, fetchall_from_query


def start_handler(bot, msg):
    bot.send_message(msg.chat.id, messages.GREETING)


def add_spending_handler(bot, msg):
    conn = connect_to_db(SQLITE_DB_FILE)
    cursor = conn.cursor()

    args = get_args(msg)
    if not args:
        bot.send_message(msg.chat.id, f"{symbols.WARNING} введите сумму траты")
        return
    try:
        spending_amount = int(args[0])
    except:
        bot.send_message(msg.chat.id, f"{symbols.WARNING} сумма траты должна быть числом")
        return

    cursor.execute(f"insert into spendings (amount) values ({spending_amount});")

    bot.send_message(msg.chat.id, f"{symbols.SUCCESS} трата успешно добавлена")
    cursor.close()
    conn.commit()


def send_stats_handler(bot, msg):
    today_date = date.today()

    query = "select amount from spendings where date(spending_date) = ?"
    today_data = fetchall_from_query(SQLITE_DB_FILE, query, today_date)
    today_spendings = calc_spendings_sum(today_data)

    query = "select amount from spendings"
    total_data = fetchall_from_query(SQLITE_DB_FILE, query)
    total_spendings = calc_spendings_sum(total_data)

    bot.send_message(msg.chat.id,
                     messages.get_stats(today_spendings, total_spendings),
                     parse_mode="Markdown")


def dev_clear_handler():
    conn = connect_to_db(SQLITE_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("delete from spendings")
    cursor.close()
    conn.commit()


def calc_spendings_sum(data):
    spendings = sum([s for t in data for s in t])
    return spendings


def get_args(msg):
    return msg.text.split()[1:]
