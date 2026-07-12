from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🃏 Карта дня")],
        [KeyboardButton(text="🔮 Росклад")],
        [KeyboardButton(text="⚙️ Налаштування")],
        [KeyboardButton(text="💳 Баланс")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Обери дію в меню нижче..."
)


def get_settings_keyboard(notify_time: str, notify_enabled: int) -> InlineKeyboardMarkup:
    status_text = "🔴 Вимкнути" if notify_enabled else "🟢 Увімкнути"

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"⏰ Час сповіщень: {notify_time}",
        callback_data="set_notify_time"
    )
    builder.button(
        text=status_text,
        callback_data="toggle_notify"
    )
    builder.button(
        text="🐛 Репортити баг",
        callback_data="report_bug"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_balance_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💶 Поповнити через Mono",
        callback_data="topup_mono"
    )
    builder.button(
        text="⭐ Поповнити Telegram Stars",
        callback_data="topup_stars_select"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📊 Статистика",
        callback_data="admin_stats"
    )
    builder.button(
        text="👥 Список користувачів",
        callback_data="admin_users_list"
    )
    builder.button(
        text="📢 Розсилка",
        callback_data="admin_broadcast"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_mono_confirm_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Зарахувати баланс",
        callback_data=f"approve_mono_{user_id}"
    )
    builder.adjust(1)
    return builder.as_markup()