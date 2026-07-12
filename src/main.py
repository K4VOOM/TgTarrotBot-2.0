import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Додати src в sys.path для імпортів
sys.path.insert(0, str(Path(__file__).parent))

from handlers import router
import database
import day_card

# Завантажити .env з кореня проекту
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено! Перевір .env файл")

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(router)

scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
scheduler.add_job(database.reset_daily_cards, "cron", hour=0, minute=0)


async def send_daily_notifications():
    """Відправляє карти дня користувачам за їх часом сповіщень."""
    current_time = datetime.now().strftime("%H:%M")
    users = database.get_users_by_notify_time(current_time)
    
    if users:
        print(f"📨 Відправка сповіщень {len(users)} користувачам в {current_time}")
        for user_tuple in users:
            user_id = user_tuple[0]
            await day_card.send_daily_card_notification(bot, user_id)
    else:
        print(f"⏰ Час {current_time}: користувачів для сповіщення не знайдено")


scheduler.add_job(send_daily_notifications, "cron", hour="*", minute="*")


async def main():
    database.init_db()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())