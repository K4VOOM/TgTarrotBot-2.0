from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards import main_menu
import database

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"🌟 Привіт, {message.from_user.first_name}! Я твій персональний Таро-бот 🃏✨ Чим можу допомогти? 🌌",
        reply_markup = main_menu
    )
    database.create_user(message.from_user.id, message.from_user.username or "no_username")
