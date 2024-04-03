import telebot

import config

bot = telebot.TeleBot(config.TOKEN, parse_mode=None)

@bot.message_handler(commands=["start", "help"])
def send_welcome(message) -> None:
    bot.send_message(message.chat.id, "sdfsdf")

if __name__ == "__main__":
    bot.infinity_polling()
