# Telegram Bot (aiogram 3.x)

Простий телеграм-бот на Python з використанням aiogram.

## Структура проєкту

```
my-bot/
├── venv/              # віртуальне середовище (не в git)
├── .env               # секрети, токен бота (не в git)
├── .gitignore
├── requirements.txt
└── bot.py             # основний файл бота
```

## Встановлення

1. Клонуй репозиторій і перейди в папку проєкту:

```bash
git clone <URL_репозиторію>
cd my-bot
```

2. Створи та активуй віртуальне середовище:

```bash
python -m venv venv

# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Встанови залежності:

```bash
pip install -r requirements.txt
```

4. Створи файл `.env` у корені проєкту та додай токен бота:

```
BOT_TOKEN=твій_токен_від_BotFather
```

## Запуск

```bash
python bot.py
```

## Залежності

- `aiogram` — асинхронний фреймворк для Telegram Bot API
- `python-dotenv` — завантаження змінних оточення з `.env`