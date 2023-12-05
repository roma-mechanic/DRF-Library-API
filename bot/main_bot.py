import telebot
from django.conf import settings
from telebot.types import Update
import requests

API_TOKEN = settings.TELEGRAM_TOKEN
BOT_CHAT_ID = settings.BOT_CHAT_ID


bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""",
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    reply_text = f"Your ID = {message.chat.id}.\n {message.text}\n Це маячня. Введіть притомніший текст"
    bot.reply_to(message, reply_text)


def telegram_bot_sendtext(bot_message):
    send_text = (
        "https://api.telegram.org/bot"
        + API_TOKEN
        + "/sendMessage?chat_id="
        + BOT_CHAT_ID
        + "&parse_mode=Markdown&text="
        + bot_message
    )

    response = requests.get(send_text)

    return response.json()
