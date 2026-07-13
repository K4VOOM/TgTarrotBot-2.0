# TgTarrotBot-2.0

Telegram-бот на Python (`aiogram 3.x`) — карта дня, три платні розклади Таро (Так/Ні, 3 карти, Кельтський Хрест) з генерацією тексту через Google Gemini, баланс, сповіщення й адмін-панель.

## Можливості

- 🃏 Карта дня з текстовою інтерпретацією (Gemini) і фото;
- 🔮 Розклади: `Так/Ні` (10 грн), `3 карти` (25 грн), `Кельтський Хрест` (50 грн) — кожен з фото карт і валідацією запиту через Gemini;
- ⏰ Щоденні сповіщення в заданий час;
- 💳 Баланс з поповненням через Mono та Telegram Stars;
- 🐛 Баг-репорти адміну;
- 🛠 Адмін-панель: статистика, список користувачів, розсилка, підтвердження оплат.

Повний опис архітектури, усіх функцій і флоу — у [`DOCS.md`](DOCS.md).

## Швидкий старт

```bash
git clone https://github.com/K4VOOM/TgTarrotBot-2.0.git
cd TgTarrotBot-2.0
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

Створи `.env` у корені проєкту:

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
ADMIN_ID=123456789
```

Запуск:

```bash
python src/main.py
```

База `data/list_users.db` створюється автоматично при першому запуску.

## Технології

`aiogram 3.x` · `APScheduler` · `SQLite` · `google-genai` · `python-dotenv`

## Структура

```text
TgTarrotBot-2.0/
├── src/            # весь код бота (детально — DOCS.md)
├── assets/         # зображення карт і README
├── data/           # SQLite база (створюється автоматично)
├── .env
├── requirements.txt
├── README.md
└── DOCS.md         # детальна документація
```

## Ліцензія

Приватний проєкт, ліцензія не вказана.
