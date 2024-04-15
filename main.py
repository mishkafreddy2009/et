import telebot
import logging
from bot_handlers import (start_handler,
                          add_spending_handler,
                          send_stats_handler,
                          dev_clear_handler)
from config import TOKEN

bot = telebot.TeleBot(TOKEN, parse_mode=None)
logger = telebot.logger

@bot.message_handler(commands=["start"])
def start(msg):
    start_handler(bot, msg)

@bot.message_handler(commands=["add"])
def add_spending(msg):
    add_spending_handler(bot, msg)

@bot.message_handler(commands=["stats"])
def send_stats(msg):
    send_stats_handler(bot, msg)

@bot.message_handler(commands=["devdel"])
def dev_clear():
    dev_clear_handler()

if __name__ == "__main__":
    # logger.setLevel(logging.DEBUG)
    bot.infinity_polling()
