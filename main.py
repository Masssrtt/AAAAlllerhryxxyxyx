from datetime import datetime, timedelta

chat_contexts_timestamps = {}

import asyncio
import platform
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import g4f
import html

# Налаштування циклів для Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Ваш токен для Telegram бота
BOT_TOKEN = "7644679484:AAGlOjZjtTMNDFeoe79B8QKWf3oBksbFr6o"

bot = telebot.TeleBot(BOT_TOKEN)

# Словник для збереження контексту чату
chat_contexts = {}

# Функція для створення клавіатури
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="🛑 Закінчити розмову"))
    return keyboard

# Функція для розбиття довгих повідомлень
def split_long_message(message, chunk_size=4096):
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

# Обробник команди /start
@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "👋 Привіт! Я ваш помічник GPT-4 🤖.\n\n"
        "Ставте будь-які запитання – я завжди радий допомогти! 🧠\n\n"
        "Відповідаю на питання про програмування, науку, технології та багато іншого! ✍️\n\n"
        "Іноді відповідь може зайняти до 5 хвилин, але я зроблю все, щоб ви залишилися задоволені! 😊\n\n"
        "Розпочнемо? 🚀",
        reply_markup=get_main_keyboard()
    )

    chat_contexts[chat_id] = [{
        "role": "system",
        "content": """
Будь ласка, використовуйте звичайні математичні символи та знаки замість HTML-форматування. Наприклад, використовуйте *, /, ^, ≤, ≥, ≠, Σ, Π, √ та інші символи безпосередньо."""
    }]

MAX_HISTORY_LENGTH = 10  # Максимальна кількість повідомлень у контексті

if len(chat_contexts[chat_id]) > MAX_HISTORY_LENGTH:
    chat_contexts[chat_id] = chat_contexts[chat_id][-MAX_HISTORY_LENGTH:]

relevant_context = "\n".join([item["content"] for item in chat_contexts[chat_id] if item["role"] != "system"])
prompt = f"Користувач спитав: {user_input}.\nІсторія бесіди:\n{relevant_context}"



# Обробник кнопки "Закінчити розмову"
@bot.message_handler(func=lambda msg: msg.text == "🛑 Закінчити розмову")
def end_chat(message):
    chat_id = message.chat.id
    if chat_id in chat_contexts:
        chat_contexts.pop(chat_id)
    bot.send_message(chat_id, """
Розмову завершено.
Якщо хочете почати нову розмову, просто поставте запитання. 😉
    """)

# Обробник будь-якого текстового повідомлення
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    user_input = message.text.strip()

    if chat_id not in chat_contexts:
        chat_contexts[chat_id] = [{
            "role": "system",
            "content": """
Будь ласка, дайте відповідь на запитання користувача чітко та зрозуміло."""
        }]

    bot.send_chat_action(chat_id, "typing")

    prompt = f"""Користувач запитав: {user_input}.
Дайте чітку та зрозумілу відповідь."""
    prompt += "\nІсторія розмови:\n" + "\n".join([item["content"] for item in chat_contexts[chat_id]])

    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )

        if isinstance(response, dict) and 'choices' in response:
            assistant_message = response['choices'][0]['message']['content']
        else:
            assistant_message = str(response)

    except Exception as e:
        assistant_message = f"Сталася помилка під час генерації відповіді: {str(e)}"

    chat_contexts[chat_id].append({"role": "assistant", "content": assistant_message})

    decoded_response = html.unescape(assistant_message)
    split_messages = split_long_message(decoded_response)

    for msg in split_messages:
        bot.send_message(chat_id, msg)
        chat_contexts_timestamps[chat_id] = datetime.now()
def cleanup_contexts():
    now = datetime.now()
    for chat_id, timestamp in list(chat_contexts_timestamps.items()):
        if now - timestamp > timedelta(hours=1):  # Контексти старше години
            chat_contexts.pop(chat_id, None)
            chat_contexts_timestamps.pop(chat_id, None)


if __name__ == "__main__":
    print("Бот запущено!")
    bot.infinity_polling()
