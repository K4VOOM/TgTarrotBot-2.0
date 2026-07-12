import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.insert(0, str(Path(__file__).parent))

import config
from handlers import router
import database
import day_card

TOKEN = config.BOT_TOKEN
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено! Перевір .env файл")

bot = Bot(token=TOKEN)
config.BOT = bot  # Зберегти bot в config

dp = Dispatcher()

dp.include_router(router)

scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
scheduler.add_job(database.reset_daily_cards, "cron", hour=0, minute=0)


async def send_daily_notifications():
    current_time = datetime.now().strftime("%H:%M")
    users = database.get_users_by_notify_time(current_time)
    
    if users:
        for user_tuple in users:
            user_id = user_tuple[0]
            await day_card.send_daily_card_notification(bot, user_id)


scheduler.add_job(send_daily_notifications, "cron", hour="*", minute="*")


async def main():
    database.init_db()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())