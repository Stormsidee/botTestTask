import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from openrouter import OpenRouter

import requests
import os
from sqlite import *

# Подключение API бота
api_key = '8504463121:AAEYCIoS8wQxq4n5AHobArIp1ua6r_jOgP4'
bot = telebot.TeleBot(api_key)

history_storage = SQLiteChatHistory()

models = [
    "deepseek/deepseek-r1-0528:free",
    "deepseek/deepseek-chat-v3.1:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "deepseek/deepseek-r1:free",
    "openai/gpt-oss-20b:free"
]

# Запрос через OpenRouter
def openrouter_response(messages):
    for model in models:
        try:
            response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "openrouter.ai",
                "X-Title": "Telegram Bot",
            },
            data=json.dumps({
                "model": model,
                "messages": messages,
            })
            )

            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            elif response.status_code == 429:
                logger.warning(f"Rate limit for model {model}, trying next...")
                continue
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return "Ошибка при обращении к API. Попробуйте позже."
                
        except Exception as e:
            logger.error(f"OpenRouter request error: {e}")
            return "Произошла ошибка при обработке запроса."
    
    

def keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn1 = KeyboardButton('Новый запрос')

    keyboard.add(btn1)

    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    history_storage.clear_history(user_id)
    bot.send_message(message.chat.id, 
                     'Привет! Я тестовый бот. Нажми "Новый запрос" чтобы начать.', 
                     reply_markup=keyboard())
    logger.info(f"User {user_id} started the bot")
    
@bot.message_handler(func=lambda message: message.text == 'Новый запрос')
def new_request(message):
    user_id = message.from_user.id
    history_storage.clear_history(user_id)

    bot.send_message(message.chat.id, 'Пожалуйста, введите ваш запрос:')
    bot.register_next_step_handler(message, process_request)

    logger.info(f"User {user_id} created a new request")


def process_request(message):
    user_id = message.from_user.id

    try:
        history_storage.add_message(message.from_user.id, 'user', message.text)
        conservation = history_storage.get_history(user_id)
        response = openrouter_response(conservation)

        history_storage.add_message(user_id, "assistant", response)
        bot.send_message(message.chat.id, response, reply_markup=keyboard())

    except Exception as e:
        logger.error(f"Error: {e}")
        bot.send_message(message.chat.id, "Ошибка!", reply_markup=keyboard())

@bot.message_handler(func=lambda message: True)
def any_message(message):
    user_id = message.from_user.id

    try:
        history_storage.add_message(message.from_user.id, 'user', message.text)
        conservation = history_storage.get_history(user_id)
        response = openrouter_response(conservation)

        history_storage.add_message(user_id, "assistant", response)
        bot.send_message(message.chat.id, response, reply_markup=keyboard())

    except Exception as e:
        logger.error(f"Error: {e}")
        bot.send_message(message.chat.id, "Ошибка!", reply_markup=keyboard())

if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling()



