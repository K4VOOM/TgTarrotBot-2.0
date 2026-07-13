from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import re

import config
import database
import day_card
import keyboards
import readings
from keyboards import main_menu

router = Router()

ADMIN_ID = config.ADMIN_ID


def is_admin(user_id: int) -> bool:
    """Перевіряє, чи є користувач адміністратором бота."""
    return user_id == ADMIN_ID


class SettingsStates(StatesGroup):
    waiting_for_time = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_payment_amount = State()


class UserStates(StatesGroup):
    waiting_for_bug_report = State()
    waiting_for_stars_amount = State()
    waiting_for_mono_screenshot = State()
    waiting_for_yes_no_question = State()
    waiting_for_three_cards_question = State()
    waiting_for_celtic_cross_question = State()


# Конфіг Mono банк
MONO_JAR_LINK = "https://send.monobank.ua/jar/2HCxsak4Bd"
MONO_CARD = "4874 1000 2567 2372"

# Ціни розкладів
READING_YES_NO_PRICE = 10.0
READING_THREE_CARDS_PRICE = 25.0
READING_CELTIC_CROSS_PRICE = 50.0


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


@router.message(F.text == "🔮 Розклад")
async def reading_menu(message: Message):
    await message.answer(
        "🔮 Вибери розклад:",
        reply_markup=keyboards.get_reading_menu_keyboard(
            READING_YES_NO_PRICE, READING_THREE_CARDS_PRICE, READING_CELTIC_CROSS_PRICE
        )
    )


@router.message(F.text == "⚙️ Налаштування")
async def setting(message: Message):
    user_data = database.read_user(message.from_user.id)
    notify_time = user_data[4]
    notify_enabled = user_data[5]

    await message.answer(
        "⚙️ Налаштування:",
        reply_markup=keyboards.get_settings_keyboard(notify_time, notify_enabled)
    )


@router.message(F.text == "💳 Баланс")
async def show_balance(message: Message):
    balance = database.get_balance(message.from_user.id)

    await message.answer(
        f"💳 Ваш баланс: {balance:.2f} ₴\n\n"
        f"Виберіть спосіб поповнення:",
        reply_markup=keyboards.get_balance_keyboard()
    )


# ===== TAROT READINGS (Розклади) =====

@router.callback_query(F.data == "reading_yes_no")
async def reading_yes_no_start(callback: CallbackQuery, state: FSMContext):
    balance = database.get_balance(callback.from_user.id)

    if balance < READING_YES_NO_PRICE:
        await callback.answer(
            f"❌ Недостатньо коштів. Потрібно {READING_YES_NO_PRICE:.0f} ₴, "
            f"на балансі {balance:.2f} ₴. Поповни баланс у меню 💳 Баланс.",
            show_alert=True
        )
        return

    await callback.message.answer(
        "☯️ Напиши своє питання так, щоб на нього можна було відповісти "
        "«так» або «ні» (наприклад: «Чи варто мені змінити роботу?»):"
    )
    await state.set_state(UserStates.waiting_for_yes_no_question)
    await callback.answer()


@router.callback_query(F.data == "reading_three_cards")
async def reading_three_cards_start(callback: CallbackQuery, state: FSMContext):
    balance = database.get_balance(callback.from_user.id)

    if balance < READING_THREE_CARDS_PRICE:
        await callback.answer(
            f"❌ Недостатньо коштів. Потрібно {READING_THREE_CARDS_PRICE:.0f} ₴, "
            f"на балансі {balance:.2f} ₴. Поповни баланс у меню 💳 Баланс.",
            show_alert=True
        )
        return

    await callback.message.answer(
        "🃏🃏🃏 Опиши ситуацію або постав питання, на яке хочеш отримати "
        "розклад «Минуле — Теперішнє — Майбутнє» "
        "(наприклад: «Що чекає на мене у стосунках?»):"
    )
    await state.set_state(UserStates.waiting_for_three_cards_question)
    await callback.answer()


@router.callback_query(F.data == "reading_celtic_cross")
async def reading_celtic_cross_start(callback: CallbackQuery, state: FSMContext):
    balance = database.get_balance(callback.from_user.id)

    if balance < READING_CELTIC_CROSS_PRICE:
        await callback.answer(
            f"❌ Недостатньо коштів. Потрібно {READING_CELTIC_CROSS_PRICE:.0f} ₴, "
            f"на балансі {balance:.2f} ₴. Поповни баланс у меню 💳 Баланс.",
            show_alert=True
        )
        return

    await callback.message.answer(
        "✝️ Кельтський Хрест — глибокий 10-карковий розклад. "
        "Опиши ситуацію або постав питання, яке хочеш проаналізувати "
        "(наприклад: «Що чекає на мої стосунки?», «Чи варто мені змінювати роботу?»):"
    )
    await state.set_state(UserStates.waiting_for_celtic_cross_question)
    await callback.answer()


@router.message(UserStates.waiting_for_yes_no_question)
async def process_yes_no_question(message: Message, state: FSMContext):
    question = message.text.strip() if message.text else ""

    if not question:
        await message.answer("❌ Надішли питання текстом.")
        return

    user_id = message.from_user.id
    balance = database.get_balance(user_id)

    if balance < READING_YES_NO_PRICE:
        await message.answer(
            f"❌ Недостатньо коштів. Потрібно {READING_YES_NO_PRICE:.0f} ₴, "
            f"на балансі {balance:.2f} ₴. Поповни баланс у меню 💳 Баланс."
        )
        await state.clear()
        return

    if not await readings.is_yes_no_question(question):
        await message.answer(
            "🤔 На це питання складно відповісти «так» чи «ні». "
            "Спробуй сформулювати його інакше, наприклад: "
            "«Чи варто мені...?» або «Чи станеться...?»"
        )
        return

    database.add_balance(user_id, -READING_YES_NO_PRICE)

    reading_text, photo_path = await readings.get_yes_no_reading(question)

    photo = FSInputFile(photo_path)
    await message.answer_photo(photo=photo)
    await message.answer(reading_text)
    await state.clear()


@router.message(UserStates.waiting_for_three_cards_question)
async def process_three_cards_question(message: Message, state: FSMContext):
    question = message.text.strip() if message.text else ""

    if not question:
        await message.answer("❌ Опиши питання чи ситуацію текстом.")
        return

    user_id = message.from_user.id
    balance = database.get_balance(user_id)

    if balance < READING_THREE_CARDS_PRICE:
        await message.answer(
            f"❌ Недостатньо коштів. Потрібно {READING_THREE_CARDS_PRICE:.0f} ₴, "
            f"на балансі {balance:.2f} ₴. Поповни баланс у меню 💳 Баланс."
        )
        await state.clear()
        return

    if not await readings.is_valid_three_cards_question(question):
        await message.answer(
            "🤔 Спробуй описати ситуацію чи питання інакше — конкретніше "
            "і по суті (наприклад: «Що чекає на мене у кар'єрі?»)."
        )
        return

    database.add_balance(user_id, -READING_THREE_CARDS_PRICE)

    reading_text, photo_paths, card_names = await readings.get_three_cards_reading(question)

    # Порядок фото в альбомі важливий: минуле -> теперішнє -> майбутнє.
    position_labels = [label for label, _ in readings.THREE_CARDS_POSITIONS]
    media_group = [
        InputMediaPhoto(
            media=FSInputFile(photo_path),
            caption=f"{label} — {card_name}"
        )
        for label, photo_path, card_name in zip(position_labels, photo_paths, card_names)
    ]

    await message.answer_media_group(media=media_group)
    await message.answer(reading_text)
    await state.clear()


@router.message(UserStates.waiting_for_celtic_cross_question)
async def process_celtic_cross_question(message: Message, state: FSMContext):
    question = message.text.strip() if message.text else ""

    if not question:
        await message.answer("❌ Опиши питання чи ситуацію текстом.")
        return

    user_id = message.from_user.id
    balance = database.get_balance(user_id)

    if balance < READING_CELTIC_CROSS_PRICE:
        await message.answer(
            f"❌ Недостатньо коштів. Потрібно {READING_CELTIC_CROSS_PRICE:.0f} ₴, "
            f"на балансі {balance:.2f} ₴. Поповни баланс у меню 💳 Баланс."
        )
        await state.clear()
        return

    if not await readings.is_valid_celtic_cross_question(question):
        await message.answer(
            "🤔 Спробуй описати ситуацію чи питання інакше — конкретніше "
            "і по суті (наприклад: «Що чекає на мої стосунки?»)."
        )
        return

    database.add_balance(user_id, -READING_CELTIC_CROSS_PRICE)

    reading_text, photo_paths, card_names = await readings.get_celtic_cross_reading(question)

    # Порядок фото в альбомі важливий — рівно 10 позицій розкладу підряд.
    position_labels = [label for label, _ in readings.CELTIC_CROSS_POSITIONS]
    media_group = [
        InputMediaPhoto(
            media=FSInputFile(photo_path),
            caption=f"{label} — {card_name}"
        )
        for label, photo_path, card_name in zip(position_labels, photo_paths, card_names)
    ]

    await message.answer_media_group(media=media_group)

    # Розпис по 10 позиціях + висновок може перевищити ліміт Telegram (4096
    # символів на повідомлення), тому надсилаємо шматками за потреби.
    if len(reading_text) > 4000:
        for i in range(0, len(reading_text), 4000):
            await message.answer(reading_text[i:i + 4000])
    else:
        await message.answer(reading_text)

    await state.clear()


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


@router.callback_query(F.data == "topup_mono")
async def topup_mono(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "💶 ПОПОВНЕННЯ ЧЕРЕЗ MONO BANK\n\n"
        "🔗 Посилання на Банку:\n"
        f"{MONO_JAR_LINK}\n\n"
        "💳 Номер картки:\n"
        f"{MONO_CARD}\n\n"
        "⚠️ ВАЖЛИВО: Суму обираєш ТИ коли скидаєш на банку.\n\n"
        "Після скидання скорочення, надішли мені скріншот оплати."
    )
    await state.set_state(UserStates.waiting_for_mono_screenshot)
    await callback.answer()


@router.message(UserStates.waiting_for_mono_screenshot)
async def process_mono_screenshot(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("❌ Надішли фото скріншоту. Спробуй ще раз.")
        return

    photo = message.photo[-1]

    user_id = message.from_user.id
    username = message.from_user.username or "anonymous"
    first_name = message.from_user.first_name or "User"

    file_id = photo.file_id

    await message.answer(
        "✅ Скріншот отримано. Адміністратор перевірить платіж."
    )

    bot = config.BOT

    admin_message = (
        f"💳 НОВИЙ ПЛАТІЖ ЧЕРЕЗ MONO:\n\n"
        f"👤 Користувач: @{username}\n"
        f"📝 Ім'я: {first_name}\n"
        f"🆔 ID: {user_id}\n\n"
        f"📎 Скріншот оплати нижче"
    )

    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=admin_message,
            reply_markup=keyboards.get_mono_confirm_keyboard(user_id)
        )
    except Exception as e:
        await message.answer(f"❌ Помилка при відправці адміну: {e}")

    await state.clear()


# ===== ADMIN COMMANDS =====

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Немає доступу. Ти не адміністратор.")
        return

    await message.answer(
        "🔐 Адмін Панель",
        reply_markup=keyboards.get_admin_keyboard()
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено!", show_alert=True)
        return

    total_users = database.count_users()

    stats_text = (
        f"📊 СТАТИСТИКА:\n\n"
        f"👥 Всього користувачів: {total_users}\n"
    )

    await callback.message.edit_text(
        stats_text,
        reply_markup=keyboards.get_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено!", show_alert=True)
        return

    users = database.get_all_users_list()

    if not users:
        users_text = "❌ Користувачів не знайдено."
    else:
        users_text = "👥 СПИСОК КОРИСТУВАЧІВ:\n\n"
        for user_id, username, balance in users:
            users_text += f"ID: {user_id} | @{username or 'anonymous'} | Баланс: {balance:.2f}₴\n"

    if len(users_text) > 4096:
        await callback.message.edit_text(
            "👥 СПИСОК КОРИСТУВАЧІВ:\n\n(Дивись нижче усіх користувачів)",
            reply_markup=keyboards.get_admin_keyboard()
        )
        for i in range(0, len(users_text), 4000):
            await callback.message.answer(users_text[i:i+4000])
    else:
        await callback.message.edit_text(
            users_text,
            reply_markup=keyboards.get_admin_keyboard()
        )

    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено!", show_alert=True)
        return

    await callback.message.answer(
        "📢 Напиши повідомлення для розсилки всім користувачам:\n\n"
        "(Все що ти напишеш далі буде розіслано)"
    )
    await state.set_state(AdminStates.waiting_for_broadcast)
    await state.update_data(broadcast_cancelled=False)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено.")
        return

    broadcast_text = message.text
    users = database.get_all_users_list()

    if not users:
        await message.answer("❌ Немає користувачів для розсилки.")
        await state.clear()
        return

    cancel_builder = keyboards.InlineKeyboardBuilder()
    cancel_builder.button(text="❌ Відмінити розсилку", callback_data="cancel_broadcast")
    cancel_markup = cancel_builder.as_markup()

    progress_msg = await message.answer(
        f"⏳ Розсилка повідомлення на {len(users)} користувачам...\n"
        f"(Натисни кнопку щоб відмінити)",
        reply_markup=cancel_markup
    )

    sent = 0
    failed = 0

    await state.update_data(broadcast_cancelled=False, progress_msg_id=progress_msg.message_id)

    bot = config.BOT

    for idx, (user_id, _, _) in enumerate(users):
        state_data = await state.get_data()
        if state_data.get("broadcast_cancelled"):
            await progress_msg.edit_text("❌ Розсилка відмінена адміністратором.")
            await state.clear()
            return

        try:
            await bot.send_message(user_id, broadcast_text)
            sent += 1
        except Exception:
            failed += 1

        if (idx + 1) % 10 == 0:
            await progress_msg.edit_text(
                f"⏳ Розсилка...\n"
                f"Оброблено: {idx + 1}/{len(users)}\n"
                f"Успішно: {sent}, Помилок: {failed}",
                reply_markup=cancel_markup
            )

    await progress_msg.edit_text(
        f"✅ Розсилка завершена!\n\n"
        f"✔️ Успішно надіслано: {sent}\n"
        f"❌ Помилок: {failed}",
        reply_markup=None
    )

    await state.clear()


@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено!", show_alert=True)
        return

    await state.update_data(broadcast_cancelled=True)
    await callback.answer("✅ Розсилка відмінена!", show_alert=True)


# ===== BUG REPORTING =====

@router.callback_query(F.data == "report_bug")
async def report_bug(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🐛 Опиши баг який ти знайшов:\n\n"
        "(Твій звіт буде відправлений адміністратору)"
    )
    await state.set_state(UserStates.waiting_for_bug_report)
    await callback.answer()


@router.message(UserStates.waiting_for_bug_report)
async def process_bug_report(message: Message, state: FSMContext):
    bug_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "anonymous"

    bot = config.BOT
    admin_message = (
        f"🐛 ЗВІТ ПРО БАГ:\n\n"
        f"👤 Користувач: @{username} (ID: {user_id})\n"
        f"📝 Опис: {bug_text}"
    )

    try:
        await bot.send_message(ADMIN_ID, admin_message)
        await message.answer("✅ Твій звіт про баг відправлено адміністратору. Спасибі!")
    except Exception as e:
        await message.answer(f"❌ Помилка при відправці: {e}")

    await state.clear()


# ===== TELEGRAM STARS PAYMENT =====

@router.callback_query(F.data == "topup_stars_select")
async def topup_stars_select(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "⭐ Введи кількість Telegram Stars для покупки:\n\n"
        "(1 ⭐ = 1₴ у баланс)\n\n"
        "Приклад: 50"
    )
    await state.set_state(UserStates.waiting_for_stars_amount)
    await callback.answer()


@router.message(UserStates.waiting_for_stars_amount)
async def process_stars_amount(message: Message, state: FSMContext):
    try:
        stars = int(message.text.strip())

        if stars <= 0:
            await message.answer("❌ Кількість повинна бути більше 0")
            return

        if stars > 10000:
            await message.answer("❌ Максимум 10000 зірочок за раз")
            return

        user_id = message.from_user.id

        bot = config.BOT

        invoice_text = (
            f"⭐ РАХУНОК ДЛЯ ОПЛАТИ:\n\n"
            f"Кількість Stars: {stars} ⭐\n"
            f"Сума до оплати: {stars} ⭐\n"
            f"Буде зараховано: {stars}₴\n\n"
            f"Натисни кнопку нижче для оплати."
        )

        await bot.send_invoice(
            chat_id=user_id,
            title=f"⭐ {stars} Telegram Stars",
            description=f"Поповнення баланс на {stars}₴",
            payload=f"stars_{stars}_{user_id}",
            provider_token="",
            currency="XTR",
            prices=[
                {"label": f"{stars} ⭐ Stars", "amount": stars}
            ]
        )

        await message.answer(invoice_text)
        await state.clear()

    except ValueError:
        await message.answer("❌ Введи число. Приклад: 50")


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment

    try:
        payload_parts = payment.invoice_payload.split("_")
        stars = int(payload_parts[1])
        user_id = int(payload_parts[2])

        if user_id == message.from_user.id:
            # Додати баланс
            database.add_balance(user_id, float(stars))

            await message.answer(
                f"✅ Платіж успішний!\n\n"
                f"⭐ Ви отримали: {stars}₴\n\n"
                f"💳 Новий баланс: {database.get_balance(user_id):.2f}₴"
            )
    except Exception as e:
        await message.answer(f"❌ Помилка при обробці платежу: {e}")


# ===== MONO PAYMENT CONFIRMATION =====

@router.callback_query(F.data.startswith("approve_mono_"))
async def approve_mono_payment(callback: CallbackQuery, state: FSMContext):
    """Адмін підтверджує платіж через Mono."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ заборонено!", show_alert=True)
        return

    user_id = int(callback.data.split("_")[2])

    await callback.message.answer(
        f"💰 Введи суму (в гривнях) яка буде зарахована користувачу (ID: {user_id}):"
    )

    await state.set_state(AdminStates.waiting_for_payment_amount)
    await state.update_data(user_id=user_id)

    await callback.answer()


@router.message(AdminStates.waiting_for_payment_amount)
async def process_payment_amount(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ заборонено.")
        return

    try:
        amount = float(message.text.strip())

        if amount <= 0:
            await message.answer("❌ Сума повинна бути більше 0")
            return

        state_data = await state.get_data()
        user_id = state_data.get("user_id")

        if not user_id:
            await message.answer("❌ Помилка: користувач не знайдений")
            await state.clear()
            return

        database.add_balance(user_id, amount)
        new_balance = database.get_balance(user_id)

        bot = config.BOT
        user_message = (
            f"✅ ПЛАТІЖ ПІДТВЕРДЖЕНО!\n\n"
            f"💰 Зараховано: {amount}₴\n"
            f"💳 Новий баланс: {new_balance:.2f}₴"
        )

        try:
            await bot.send_message(user_id, user_message)
        except Exception:
            pass  # Користувач міг заблокувати бота — не критично

        await message.answer(
            f"✅ ПЛАТІЖ ЗАРАХОВАНО:\n\n"
            f"👤 Користувач ID: {user_id}\n"
            f"💰 Сума: {amount}₴\n"
            f"💳 Новий баланс користувача: {new_balance:.2f}₴"
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введи число. Приклад: 100")