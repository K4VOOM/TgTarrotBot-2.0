from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🃏 Карта дня")],
        [KeyboardButton(text="🔮 Розклад")],
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


def get_reading_menu_keyboard(
    yes_no_price: float, three_cards_price: float, celtic_cross_price: float
) -> InlineKeyboardMarkup:
    """Клавіатура вибору типу розкладу в меню '🔮 Розклад'."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"☯️ Так / Ні — {yes_no_price:.0f} грн",
        callback_data="reading_yes_no"
    )
    builder.button(
        text=f"🃏🃏🃏 Розклад на 3 карти — {three_cards_price:.0f} грн",
        callback_data="reading_three_cards"
    )
    builder.button(
        text=f"✝️ Кельтський Хрест — {celtic_cross_price:.0f} грн",
        callback_data="reading_celtic_cross"
    )
    builder.adjust(1)
    return builder.as_markup()