from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import re

import keyboards

from keyboards import main_menu
import database
import day_card

router = Router()


class SettingsStates(StatesGroup):
    waiting_for_time = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"🌟 Привіт, {message.from_user.first_name}! Я твій персональний Таро-бот 🃏✨ Чим можу допомогти? 🌌",
        reply_markup=main_menu
    )
    database.create_user(message.from_user.id, message.from_user.username or "no_username")


@router.message(F.text == "🃏 Карта дня")
async def daily_card(message: Message):
    message_text, photo_path = await day_card.get_day_card_for_user(message.from_user.id)

    photo = FSInputFile(photo_path)
    await message.answer_photo(photo=photo)
    await message.answer(message_text)


@router.message(F.text == "⚙️ Налаштування")
async def setting(message: Message):
    user_data = database.read_user(message.from_user.id)
    notify_time = user_data[4]
    notify_enabled = user_data[5]

    await message.answer(
        "⚙️ Налаштування:",
        reply_markup=keyboards.get_settings_keyboard(notify_time, notify_enabled)
    )


@router.callback_query(F.data == "toggle_notify")
async def toggle_notify(callback: CallbackQuery):
    new_state = database.toggle_notify_enabled(callback.from_user.id)
    user_data = database.read_user(callback.from_user.id)
    notify_time = user_data[4]

    await callback.message.edit_reply_markup(
        reply_markup=keyboards.get_settings_keyboard(notify_time, new_state)
    )
    emoji = "✅" if new_state else "❌"
    await callback.answer(
        f"{emoji} " + ("Увімкнено!" if new_state else "Вимкнено!")
    )


@router.callback_query(F.data == "set_notify_time")
async def ask_notify_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("⏰ Введи час (ГГ:ХХ, наприклад 09:30):")
    await state.set_state(SettingsStates.waiting_for_time)
    await callback.answer()


@router.message(SettingsStates.waiting_for_time)
async def save_notify_time(message: Message, state: FSMContext):
    time_str = message.text.strip()

    if not re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", time_str):
        await message.answer("❌ Невірний формат. Введи ГГ:ХХ (09:30)")
        return

    database.set_notify_time(message.from_user.id, time_str)
    await state.clear()

    user_data = database.read_user(message.from_user.id)
    notify_enabled = user_data[5]

    await message.answer(
        f"✅ Час сповіщень встановлено на {time_str}",
        reply_markup=keyboards.get_settings_keyboard(time_str, notify_enabled)
    )