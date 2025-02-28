import os
import logging
from aiogram import Bot, Dispatcher, executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import ar

load_dotenv()

# Токени та налаштування
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен бота
BRAWL_API_TOKEN = os.getenv("BRAWL_API_TOKEN")  # API-ключ Brawl Stars
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID каналу, де оновлюється пост
POST_ID = int(os.getenv("POST_ID"))  # ID поста для оновлення

# ID клубів Brawl Stars
CLUBS = {
    "KT the champion": "2RPOCQJ92",
    "KT Academy": "2YCP2QRL9",
    "KT Trailblazers": "2JJ8YVJGC",
}

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Ініціалізація клієнта Brawl Stars API
client = ar.Client(BRAWL_API_TOKEN)

# Функція для отримання даних клубу
async def get_club_info(club_tag):
    try:
        club = await client.get_club(club_tag)
        return {
            "name": club.name,
            "trophies": club.trophies,
            "requiredTrophies": club.required_trophies,
        }
    except ar.errors.RequestError as e:
        logging.error(f"Помилка отримання даних: {e}")
        return None

# Оновлення поста в Telegram-каналі
async def update_post():
    message = "😎Вітаємо в імперії клубів КТ!\nМи входимо до гільдії Sun Guild☀️!\n\nНаші клуби:\n"
    for club_name, club_tag in CLUBS.items():
        info = await get_club_info(club_tag)
        if info:
            message += f"🏆{info['trophies']}\n🏆{info['requiredTrophies']}+\n💬ТГ Чат: @KT_the_champion\n\n"
    
    await bot.edit_message_text(chat_id=CHANNEL_ID, message_id=POST_ID, text=message)
    logging.info("Пост оновлено!")

# Запускаємо оновлення щогодини
scheduler.add_job(lambda: dp.loop.create_task(update_post()), "interval", hours=1)
scheduler.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
