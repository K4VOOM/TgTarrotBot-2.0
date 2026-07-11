from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from keyboards import main_menu
import database
import day_card

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"🌟 Привіт, {message.from_user.first_name}! Я твій персональний Таро-бот 🃏✨ Чим можу допомогти? 🌌",
        reply_markup = main_menu
    )
    database.create_user(message.from_user.id, message.from_user.username or "no_username")

@router.message(F.text == "Карта дня")
async def daily_card(message: Message):
    message_text, photo_path = await day_card.get_day_card_for_user(message.from_user.id)

    photo = FSInputFile(photo_path)
    await message.answer_photo(photo=photo)
    await message.answer(message_text)