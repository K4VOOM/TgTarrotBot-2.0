import asyncio
import os
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from handlers import router
import database

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено! Перевір .env файл")

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(router)

scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
scheduler.add_job(database.reset_daily_cards, "cron", hour=0, minute=0)


async def main():
    database.init_db()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())