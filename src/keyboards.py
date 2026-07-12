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
    builder.adjust(1)
    return builder.as_markup()