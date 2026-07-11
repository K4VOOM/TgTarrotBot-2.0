# TgTarrotBot-2.0


## Структура проєкту

```
TgTarrotBot-2.0/
├── .venv/                      # Віртуальне середовище Python
├── card_photo/                 # Папка із зображеннями карт Таро
│   └── classic/                # Класична колода
│       ├── Cups/               # Кубки
│       ├── Major_Arcana/       # Старші Аркани
│       ├── Pentacles/          # Пентаклі
│       ├── Swords/             # Мечі
│       └── Wands/              # Жезли
├── readme_photo/               # Зображення для документації README
├── .env                        # Файл із конфігураційними токенами та змінними оточення
├── .gitignore                  # Список файлів, що ігноруються Git
├── database.py                 # Логіка та налаштування роботи з базою даних SQLite
├── handlers.py                 # Обробники текстових повідомлень та callback-запитів
├── keyboards.py                # Конструктор клавіатур бота
├── list_users.db               # Файл бази даних SQLite
├── main.py                     # Головний файл для запуску асинхронного бота
├── README.md                   # Документація проєкту
├── requirements.txt            # Список залежностей та бібліотек
└── tarrot_data.py              # Словник із назвами, описами та шляхами до карт
```

#діаграма проєкту

![Діаграма проєкту](readme_photo/project_diagram.png)

## Встановлення

1. Клонуй репозиторій і перейди в папку проєкту:

```bash
git clone <https://github.com/K4VOOM/TgTarrotBot-2.0.git>
cd TgTarrotBot-2.0
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
python main.py
```

## Залежності

- `aiogram` — асинхронний фреймворк для Telegram Bot API
- `python-dotenv` — завантаження змінних оточення з `.env`
