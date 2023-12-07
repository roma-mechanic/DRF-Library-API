import requests
import telebot
from django.conf import settings

from user.models import UserProfile

API_TOKEN = settings.TELEGRAM_TOKEN
BOT_CHAT_ID = settings.BOT_CHAT_ID

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        """\
Hi there, I am LibraryBot.
I will register you now. Please enter your username that you used when registering in our library.\
""",
    )
    bot.register_next_step_handler(message, get_username)


def get_username(message):
    username = message.text.strip().lower().capitalize()
    user = UserProfile.objects.get(username=username)
    if user:
        user.telebot_chat_ID = message.chat.id
        user.save()
        bot.reply_to(
            message,
            f"Hi {username}, You are registered. Your chat_id {message.chat.id}",
        )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    reply_text = f"Your ID = {message.chat.id}.\n {message.text}\n "
    bot.reply_to(message, reply_text)


def telegram_bot_sendtext(bot_message, chat_id):
    send_text = (
        "https://api.telegram.org/bot"
        + API_TOKEN
        + "/sendMessage?chat_id="
        + chat_id
        + "&parse_mode=Markdown&text="
        + bot_message
    )

    response = requests.get(send_text)

    return response.json()
