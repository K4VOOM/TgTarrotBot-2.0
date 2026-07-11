# TgTarrotBot-2.0

Асинхронний Telegram бот на Python з AI-інтеграцією Google Gemini та SQLite.

## Архітектура

**Tech Stack:**
- `aiogram 3.x` — асинхронна бібліотека для Telegram Bot API
- `google-generativeai` — Google Gemini API для генерації текстів
- `apscheduler` — асинхронний scheduler для планування завдань
- `SQLite 3` — локальна БД для збереження стану користувачів
- `Python 3.10+` — asyncio, FSM (Finite State Machine)

**Дизайн:**
- Event loop: aiogram dispatcher + apscheduler co-exist
- Message polling, callback queries, FSM для обробки вводу
- Scheduler запускається кожну хвилину, перевіряє БД на предмет розсилок
- Усі I/O операції асинхронні (БД, API запити)

## Структура файлів

```
TgTarrotBot-2.0/
├── main.py              # Entry point: bot initialization, dispatcher, scheduler
├── handlers.py          # Router з усіма message/callback handlers
├── keyboards.py         # ReplyKeyboardMarkup, InlineKeyboardMarkup builders
├── database.py          # CRUD для users table, helper queries
├── day_card.py          # Генерація карт, розсилка, Gemini wrapper
├── gemini_client.py     # Google Gemini API client
├── tarrot_data.py       # Dict структура карт (назви, описи, шляхи до фото)
├── card_photo/          # Зображення карт по категоріях
├── .env                 # BOT_TOKEN, GEMINI_API_KEY (не комітити)
├── list_users.db        # SQLite файл (генерується автоматично)
└── requirements.txt     # Залежності
```

## Схема БД

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    day_card_mes INTEGER DEFAULT 0,         -- чи юзер отримав карту дня (flag)
    today_give_card TEXT DEFAULT NULL,      -- система назва поточної карти
    notify_time TEXT DEFAULT '09:00',       -- час розсилки (ГГ:ХХ, 24-bit format)
    notify_enabled INTEGER DEFAULT 1        -- 1 = ON, 0 = OFF
)
```

**Типові операції:**
- INSERT OR IGNORE при /start
- SELECT для read_user(user_id)
- UPDATE для set_notify_time, set_today_card, toggle_notify_enabled
- SELECT для send_daily_notifications (query по notify_time)

## Основні Flow

### 1. /start → користувач створюється
```
Handler: cmd_start()
  └─> database.create_user(user_id, username)
      └─> INSERT OR IGNORE into users
  └─> reply з main_menu
```

### 2. "🃏 Карта дня" → генерація та відправка
```
Handler: daily_card()
  └─> day_card.get_day_card_for_user(user_id)
      ├─> database.read_user(user_id)
      ├─> IF today_give_card IS NULL:
      │   └─> tarrot_data.get_random_card()
      │   └─> database.set_today_card(user_id, card_name)
      ├─> tarrot_data.get_something_for_card(system_name, "name/description/classic_photo")
      └─> gemini_client.generate_text(prompt_with_card_data)
  └─> bot.send_photo(photo) + bot.send_message(message_text)
```

### 3. Налаштування сповіщень → FSM
```
Handler: setting()
  └─> reply із inline keyboards (toggle + time setter)

Callback: toggle_notify()
  └─> database.toggle_notify_enabled(user_id)  [1-notify_enabled]
  └─> refresh keyboard

Callback: set_notify_time()
  └─> state.set_state(SettingsStates.waiting_for_time)
  └─> user вводит час

Handler: save_notify_time(message, state)
  ├─> validate regex: ([01]\d|2[0-3]):([0-5]\d)
  ├─> database.set_notify_time(user_id, time_str)
  └─> state.clear()
```

### 4. Автоматичні сповіщення → Scheduler
```
Job: send_daily_notifications()  [runs every minute]
  ├─> current_time = datetime.now().strftime("%H:%M")
  ├─> users = database.get_users_by_notify_time(current_time)
  │   └─> SELECT user_id WHERE notify_enabled=1 AND notify_time=?
  ├─> FOR each user_id:
  │   └─> day_card.send_daily_card_notification(bot, user_id)
  │       ├─> day_card.get_day_card_for_user(user_id)  [sets card if null]
  │       └─> bot.send_photo() + bot.send_message()
  └─> print() на консоль
```

**Щодня о 00:00:**
```
Job: database.reset_daily_cards()
  └─> UPDATE users SET today_give_card=NULL, day_card_mes=0
```

## API Функції

### database.py
```python
def create_user(user_id: int, username: str)
def read_user(user_id: int) -> tuple[6 items]
def read_all_users() -> list[tuple]
def set_day_card_true(user_id: int)
def set_today_card(user_id: int, card_name: str)
def delete_user(user_id: int)
def reset_daily_cards()
def set_notify_time(user_id: int, time_str: str)
def toggle_notify_enabled(user_id: int) -> int  # returns new state
def get_users_by_notify_time(notify_time: str) -> list[tuple]
```

### day_card.py
```python
async def generate_day_card_message(card_name: str, card_description: str) -> str
async def get_day_card_for_user(user_id: int) -> tuple[str, str]  # (message_text, photo_path)
async def send_daily_card_notification(bot, user_id: int) -> bool
```

### gemini_client.py
```python
async def generate_text(prompt: str) -> str
```

### handlers.py (Router)
```python
@router.message(Command("start"))
async def cmd_start(message: Message)

@router.message(F.text == "🃏 Карта дня")
async def daily_card(message: Message)

@router.message(F.text == "⚙️ Налаштування")
async def setting(message: Message)

@router.callback_query(F.data == "toggle_notify")
async def toggle_notify(callback: CallbackQuery)

@router.callback_query(F.data == "set_notify_time")
async def ask_notify_time(callback: CallbackQuery, state: FSMContext)

@router.message(SettingsStates.waiting_for_time)
async def save_notify_time(message: Message, state: FSMContext)
```

## Встановлення і запуск

```bash
# 1. Clone & venv
git clone https://github.com/K4VOOM/TgTarrotBot-2.0.git
cd TgTarrotBot-2.0
python -m venv venv
source venv/bin/activate  # або venv\Scripts\activate на Windows

# 2. Install deps
pip install -r requirements.txt

# 3. Configure .env
echo "BOT_TOKEN=..." > .env
echo "GEMINI_API_KEY=..." >> .env

# 4. Run
python main.py
```

## Конфіг

**.env:**
```
BOT_TOKEN=123456:ABC-DEF1...
GEMINI_API_KEY=AIzaSy...
```

**Scheduler timezone:** `Europe/Kyiv` у main.py

**Prompt для Gemini:** зберігається як PROMPT_TEMPLATE у day_card.py (структура: назва карти + здоров'я/фінанси/відносини + афірмація)

## Поточний стан

✅ **Реалізовано:**
- ✅ Message routing (start, daily card, settings)
- ✅ Callback query handling (toggle, time setter)
- ✅ FSM для вводу часу з валідацією
- ✅ SQLite CRUD операції
- ✅ Scheduler job з поміхутною розсилкою
- ✅ Gemini інтеграція для генерації описів
- ✅ Структура карт з фото

⏳ **TODO/WIP:**
- 🔮 Росклад функціонал (Spread queries, layout logic)
- 💳 Баланс/LoyaltyPoints система
- 📊 Analytics (статистика карт)
- 🗣️ Мультимова підтримка
- 🔐 Error handling/logging

## Розширення

Для додавання функціоналу:

1. **Новий message handler** → `handlers.py`, додати до router
2. **Нові БД операції** → `database.py`, update schema якщо потрібно
3. **Нові UI елементи** → `keyboards.py`
4. **Новий scheduler job** → `main.py`, `scheduler.add_job(...)`

Весь код асинхронний, використовуйте `await` для I/O операцій.

## Залежності версії

```
aiogram>=3.0
google-generativeai
apscheduler
python-dotenv
```
