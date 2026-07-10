from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Карта дня")],
        [KeyboardButton(text="Зробити росклад")],
        [KeyboardButton(text="Налаштування")],
        [KeyboardButton(text="Баланс")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Обери дію в меню нижче..."
)