# TgTarrotBot-2.0 — детальна документація

Цей документ описує архітектуру, кожен файл, кожну функцію, схему БД,
FSM-стани, callback-дані, промпти до Gemini і повні сценарії роботи бота.
Для короткого огляду й швидкого старту дивись [`README.md`](README.md).

## Зміст

1. [Загальна архітектура](#загальна-архітектура)
2. [Змінні середовища](#змінні-середовища)
3. [`src/config.py`](#srcconfigpy)
4. [`src/database.py`](#srcdatabasepy)
5. [`src/tarrot_data.py`](#srctarrot_datapy)
6. [`src/gemini_client.py`](#srcgemini_clientpy)
7. [`src/keyboards.py`](#srckeyboardspy)
8. [`src/day_card.py`](#srcday_cardpy)
9. [`src/readings.py`](#srcreadingspy)
10. [`src/handlers.py`](#srchandlerspy)
11. [`src/main.py`](#srcmainpy)
12. [Повні сценарії (флоу)](#повні-сценарії-флоу)
13. [FSM-стани — зведена таблиця](#fsm-стани--зведена-таблиця)
14. [Callback-дані — зведена таблиця](#callback-дані--зведена-таблиця)
15. [Відомі обмеження та ідеї на майбутнє](#відомі-обмеження-та-ідеї-на-майбутнє)

---

## Загальна архітектура

```
Telegram  <──polling──>  aiogram Dispatcher (main.py)
                              │
                              ├── router (handlers.py)  ── усі message/callback обробники
                              │       │
                              │       ├── database.py     — SQLite (users, баланс, налаштування)
                              │       ├── keyboards.py    — reply/inline клавіатури
                              │       ├── day_card.py     — сценарій "карта дня"
                              │       └── readings.py     — сценарії розкладів (Так/Ні, 3 карти, Кельтський Хрест)
                              │               │
                              │               ├── tarrot_data.py   — колода карт (78 шт.) + шляхи до фото
                              │               └── gemini_client.py — виклики Google Gemini (rate-limited)
                              │
                              └── APScheduler (main.py) — щоденні сповіщення + опівнічний ресет
```

Принцип шарів: `handlers.py` ніколи напряму не працює з SQLite-курсорами чи
Gemini API — він завжди йде через `database.py` / `day_card.py` / `readings.py`,
які, у свою чергу, використовують `tarrot_data.py` і `gemini_client.py`.
Це дозволяє міняти джерело карт або LLM-провайдера, не чіпаючи `handlers.py`.

---

## Змінні середовища

Файл `.env` у корені проєкту (див. `config.py`, що його завантажує):

| Змінна            | Обов'язкова | За замовчуванням         | Опис                                   |
|-------------------|:-----------:|---------------------------|-----------------------------------------|
| `BOT_TOKEN`       | так         | —                          | Токен Telegram-бота від @BotFather      |
| `GEMINI_API_KEY`  | так         | —                          | Ключ Google GenAI (Gemini)              |
| `GEMINI_MODEL`    | ні          | `gemini-3.1-flash-lite`    | Назва моделі Gemini                     |
| `ADMIN_ID`        | ні (0)      | `0`                        | Telegram ID адміністратора              |
| `GEMINI_RPM_LIMIT`| ні          | `15`                       | Ліміт запитів/хв до Gemini (rate limiter в `gemini_client.py`) |

Якщо `BOT_TOKEN` або `GEMINI_API_KEY` відсутні — бот кине `ValueError` при
старті (`main.py` / `gemini_client.py` відповідно).

---

## `src/config.py`

Центральна точка конфігурації. Завантажує `.env` через `python-dotenv`
за абсолютним шляхом (`PROJECT_ROOT / ".env"`), незалежно від того, з якої
директорії запущено скрипт.

| Ім'я           | Тип           | Опис                                                                 |
|----------------|---------------|------------------------------------------------------------------------|
| `PROJECT_ROOT` | `Path`        | Корінь проєкту (батько `src/`)                                        |
| `BOT`          | `Bot \| None` | Інстанс `aiogram.Bot`; встановлюється в `main.py` після створення бота, щоб `handlers.py` міг надсилати повідомлення поза контекстом обробника (розсилка, підтвердження оплат) |
| `ADMIN_ID`     | `int`         | Telegram ID адміністратора                                             |
| `BOT_TOKEN`    | `str \| None` | Токен бота                                                             |
| `GEMINI_API_KEY` | `str \| None` | Ключ Gemini API                                                     |
| `GEMINI_MODEL` | `str`         | Модель Gemini за замовчуванням                                        |

Усі інші модулі (`database.py`, `gemini_client.py`, `handlers.py`) імпортують
`config` і читають значення звідси — змінні середовища напряму більше ніде
не читаються (окрім `GEMINI_RPM_LIMIT` у `gemini_client.py`).

---

## `src/database.py`

Увесь доступ до SQLite. База лежить у `data/list_users.db` (шлях будується
відносно кореня проєкту, портативно).

### Підключення

```python
@contextmanager
def get_connection():
```

Контекстний менеджер, що **гарантовано закриває з'єднання** через
`finally: conn.close()`. Це важливо: сам `sqlite3.Connection`, використаний
як `with`-менеджер, лише комітить/відкочує транзакцію, але **не закриває**
з'єднання — тому цей шар обгортки обов'язковий, інакше з'єднання
накопичуються.

### Таблиця `users`

```sql
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    day_card_mes INTEGER DEFAULT 0,
    today_give_card TEXT DEFAULT NULL,
    notify_time TEXT DEFAULT '09:00',
    notify_enabled INTEGER DEFAULT 1,
    balance REAL DEFAULT 0.0
);
```

| Колонка           | Опис                                                                 |
|-------------------|--------------------------------------------------------------------|
| `user_id`         | Telegram user id, первинний ключ                                    |
| `username`        | Telegram @username (може бути NULL)                                 |
| `day_card_mes`    | 1, якщо карта дня вже була відправлена сьогодні (авто-сповіщенням)  |
| `today_give_card` | Системний ключ карти (напр. `the_fool`), виданої сьогодні як карта дня |
| `notify_time`     | Час щоденного сповіщення у форматі `ГГ:ХХ`                          |
| `notify_enabled`  | 1/0 — чи увімкнені сповіщення                                       |
| `balance`         | Баланс користувача в гривнях (`REAL`)                               |

При старті `init_db()` додатково намагається виконати
`ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0` і ловить
`sqlite3.OperationalError`, якщо колонка вже існує — це дозволяє безпечно
оновлювати вже розгорнуту БД зі старої версії схеми без ручної міграції.

### Функції

| Функція                                  | Сигнатура / повертає                          | Опис |
|-------------------------------------------|------------------------------------------------|------|
| `init_db()`                               | `None`                                          | Створює таблицю, якщо її нема, і додає колонку `balance` за потреби |
| `create_user(user_id, username)`          | `None`                                          | `INSERT OR IGNORE` — не дублює існуючого користувача |
| `read_user(user_id)`                      | `tuple \| None`                                 | `(user_id, username, day_card_mes, today_give_card, notify_time, notify_enabled, balance)` |
| `read_all_users()`                        | `list[tuple]`                                   | Усі колонки всіх користувачів (наразі не використовується в `handlers.py`, залишена як утиліта) |
| `set_day_card_true(user_id)`              | `None`                                          | Ставить `day_card_mes = 1` (наразі не використовується в поточному флоу — карта дня видається за запитом, без прапорця "вже показано") |
| `delete_user(user_id)`                    | `None`                                          | Видаляє користувача (утиліта, ніде не викликається) |
| `set_today_card(user_id, card_name)`      | `None`                                          | Записує системний ключ карти дня |
| `reset_daily_cards()`                     | `None`                                          | `today_give_card = NULL`, `day_card_mes = 0` для всіх — викликається щоночі о 00:00 |
| `set_notify_time(user_id, time_str)`      | `None`                                          | Зберігає новий час сповіщень |
| `toggle_notify_enabled(user_id)`          | `int` (нове значення 0/1)                       | `notify_enabled = 1 - notify_enabled`, повертає результат однією транзакцією |
| `get_users_by_notify_time(notify_time)`   | `list[tuple[int]]`                              | `user_id` усіх, у кого `notify_enabled=1` і `notify_time` збігається — використовується scheduler'ом раз на хвилину |
| `get_balance(user_id)`                    | `float`                                         | Повертає 0.0, якщо користувача нема |
| `set_balance(user_id, balance)`           | `None`                                          | Жорстко встановлює баланс |
| `add_balance(user_id, amount)`            | `None`                                          | `get_balance` + `set_balance`; `amount` може бути від'ємним (списання за розклад) |
| `count_users()`                           | `int`                                           | Для адмінської статистики |
| `get_all_users_list()`                    | `list[tuple[user_id, username, balance]]`       | Для адмінського списку користувачів, відсортовано за `user_id` |

---

## `src/tarrot_data.py`

Статична колода з 78 карт Таро (22 Старші Аркани + 56 Молодших по мастях
Cups/Pentacles/Swords/Wands). Кожен запис у словнику `tarrot_desk`:

```python
tarrot_desk = {
    "the_fool": {
        "name": "Блазень",
        "description": "0. Блазень. Карта позначає...",
        "classic_photo": "card_photo/classic/Major_Arcana/the_fool.jpg",
    },
    ...
}
```

`classic_photo` — шлях **відносно** `assets/` (абсолютний шлях будується
через `ASSETS_PATH = PROJECT_ROOT / "assets"`).

### Функції

| Функція                              | Повертає         | Опис |
|----------------------------------------|------------------|------|
| `get_random_card()`                   | `str`            | Один випадковий системний ключ (`random.choice`) — використовується для карти дня і розкладу "Так/Ні" |
| `get_random_unique_cards(count)`      | `list[str]`      | `count` **різних** ключів без повторів (`random.sample`) — використовується для розкладів "3 карти" (count=3) і "Кельтський Хрест" (count=10) |
| `get_something_for_card(system_name, something)` | `str` | Дістає одне поле карти (`"name"`, `"description"`, `"classic_photo"`); для `"classic_photo"` автоматично повертає **абсолютний** шлях (`str(ASSETS_PATH / value)`), готовий для `FSInputFile` |

---

## `src/gemini_client.py`

Тонка обгортка над `google-genai` з вбудованим rate-limiter'ом (щоб не
впертися в ліміт запитів/хвилину Gemini API).

### `RateLimiter`

Ковзне вікно на 60 секунд, реалізоване через `collections.deque` міток часу
й `asyncio.Lock`. Метод `acquire()`:
1. Прибирає з черги мітки старші за 60 секунд.
2. Якщо в черзі менше за `RPM_LIMIT` — одразу дозволяє запит і додає мітку.
3. Інакше — рахує, скільки чекати до звільнення найстарішого слоту, і засинає.

Глобальний інстанс `_rate_limiter = RateLimiter(RPM_LIMIT)` — один на весь
процес, тому всі виклики `generate_text()` (з `day_card.py` і `readings.py`)
діляться одним і тим самим лімітом.

### `generate_text(prompt, model_name=None) -> str`

1. Чекає слот у rate limiter'і.
2. Викликає `client.models.generate_content(...)` у окремому треді
   (`asyncio.to_thread`, бо SDK синхронний) з моделлю `model_name or DEFAULT_MODEL`.
3. Повертає `response.text.strip()`.

Це єдина точка входу до LLM у всьому проєкті — і `day_card.py`, і
`readings.py` викликають лише цю функцію з різними промптами.

---

## `src/keyboards.py`

Усі клавіатури бота (reply + inline), побудовані через
`aiogram.utils.keyboard.InlineKeyboardBuilder`.

| Об'єкт / функція                                        | Тип        | Опис |
|-----------------------------------------------------------|------------|------|
| `main_menu`                                                | `ReplyKeyboardMarkup` (константа) | Головне меню: `🃏 Карта дня`, `🔮 Розклад`, `⚙️ Налаштування`, `💳 Баланс` |
| `get_settings_keyboard(notify_time, notify_enabled)`       | `InlineKeyboardMarkup` | Кнопки: час сповіщень, увімкнути/вимкнути (текст кнопки залежить від поточного стану), баг-репорт |
| `get_balance_keyboard()`                                   | `InlineKeyboardMarkup` | Mono / Telegram Stars |
| `get_admin_keyboard()`                                     | `InlineKeyboardMarkup` | Статистика / список користувачів / розсилка |
| `get_mono_confirm_keyboard(user_id)`                       | `InlineKeyboardMarkup` | Одна кнопка "Зарахувати баланс" з `user_id`, зашитим у `callback_data=f"approve_mono_{user_id}"` — надсилається адміну разом зі скріншотом оплати |
| `get_reading_menu_keyboard(yes_no_price, three_cards_price, celtic_cross_price)` | `InlineKeyboardMarkup` | 3 кнопки розкладів із цінами в тексті кнопки |

---

## `src/day_card.py`

Логіка "карти дня" — і для ручного запиту (`🃏 Карта дня`), і для
автоматичних сповіщень за розкладом.

### `PROMPT_TEMPLATE`

Жорстко структурований промпт: назва й опис карти → Gemini повертає готовий
текст із блоками "Здоров'я / Фінанси / Відносини / Афірмація дня" (без
markdown-розмітки, українською, на "ти").

### Функції

| Функція                                             | Повертає                    | Опис |
|-------------------------------------------------------|------------------------------|------|
| `generate_day_card_message(card_name, card_description)` | `str`                    | Підставляє карту в `PROMPT_TEMPLATE` і викликає `gemini_client.generate_text` |
| `get_day_card_for_user(user_id)`                      | `(message_text, photo_path)` | Головна функція. Читає `today_give_card` з БД; якщо `None` — тягне нову випадкову карту й **зберігає** її в БД (`set_today_card`), щоб повторний виклик того ж дня повернув ту саму карту. Потім генерує текст і повертає разом зі шляхом до фото |
| `send_daily_card_notification(bot, user_id)`          | `bool`                       | Обгортка для scheduler'а: викликає `get_day_card_for_user`, надсилає фото + текст напряму через `bot.send_photo`/`send_message` (без `Message`-контексту, бо це не відповідь на команду користувача). Ловить `Exception` і повертає `False`, щоб один невдалий користувач (напр. заблокував бота) не зупиняв розсилку іншим |

---

## `src/readings.py`

Логіка всіх трьох розкладів. Спільний патерн для кожного розкладу:

1. **Classify-промпт** — окремий, дешевий виклик Gemini, який відповідає
   рівно одним словом (`ТАК`/`НІ`), чи запит користувача взагалі підходить
   для цього типу розкладу. Це і є "перевірка правильності запиту", про яку
   йшлося в постановці задачі — вона виконується Gemini, а не regex/ключовими
   словами, тому розуміє сенс, а не тільки форму питання.
2. **Answer-промпт** — розгорнутий виклик з описом усіх витягнутих карт,
   що повертає готовий, строго структурований текст.
3. Python-функція, яка тягне карти (`tarrot_data`), збирає промпт і формує
   фінальний результат — текст + шляхи до фото (+ назви карт, де потрібно
   для підписів).

### Так / Ні

| Об'єкт                                             | Опис |
|------------------------------------------------------|------|
| `YES_NO_CLASSIFY_PROMPT_TEMPLATE`                    | Просить Gemini визначити, чи питання закрите (можлива відповідь так/ні) |
| `YES_NO_ANSWER_PROMPT_TEMPLATE`                      | Дає картy + опис, просить обрати ТАК/НІ і додати пояснення до 15 слів, одним рядком |
| `is_yes_no_question(question) -> bool`               | `True`, якщо відповідь Gemini починається з "ТАК" |
| `generate_yes_no_answer(card_name, card_description, question) -> str` | Рядок виду `"ТАК — пояснення"` |
| `get_yes_no_reading(question) -> (message_text, photo_path)` | Тягне 1 випадкову карту (`get_random_card`), генерує рядок-відповідь, збирає фінальний текст:<br>`🔮 Ваше питання: ...`<br>`` `` <br>`🃏 Карта відповіді:`<br>`ТАК — ...` |

### Розклад на 3 карти (Минуле — Теперішнє — Майбутнє)

| Об'єкт                                             | Опис |
|------------------------------------------------------|------|
| `THREE_CARDS_POSITIONS`                               | `[("🕰 Минуле", "past"), ("✨ Теперішнє", "present"), ("🔮 Майбутнє", "future")]` — порядок визначає порядок фото в альбомі |
| `THREE_CARDS_CLASSIFY_PROMPT_TEMPLATE`               | Перевіряє, чи запит осмислений і стосується життєвої ситуації (ширше, ніж просто так/ні) |
| `THREE_CARDS_ANSWER_PROMPT_TEMPLATE`                 | Дає всі 3 карти одразу, просить розпис по кожній позиції + загальний висновок |
| `is_valid_three_cards_question(question) -> bool`    | Аналогічно `is_yes_no_question`, але для іншого промпту |
| `get_three_cards_reading(question) -> (message_text, photo_paths, card_names)` | Тягне 3 **різні** карти (`get_random_unique_cards(3)`) у порядку минуле→теперішнє→майбутнє, повертає текст + список фото + список назв (в тому самому порядку — критично для правильних підписів в альбомі) |

### Кельтський Хрест (10 карт)

| Об'єкт                                             | Опис |
|------------------------------------------------------|------|
| `CELTIC_CROSS_POSITIONS`                              | 10 пар `(emoji, назва_позиції)` в порядку класичного розкладу: Поточна ситуація → Перешкода → Минуле → Найближче майбутнє → Свідоме → Підсвідоме → Сам кверент → Зовнішні впливи → Надії і страхи → Результат |
| `CELTIC_CROSS_CLASSIFY_PROMPT_TEMPLATE`              | Перевіряє, чи запит підходить для глибокого аналітичного розкладу (не порожній, не спам, стосується життєвої ситуації) |
| `CELTIC_CROSS_ANSWER_PROMPT_TEMPLATE`                | Найбільший промпт у проєкті — передає всі 10 карт з позиціями й описами одночасно, вимагає розпис по кожній із 10 позицій у строго заданому форматі + `✨ Висновок` + `👉 Порада` (без markdown) |
| `is_valid_celtic_cross_question(question) -> bool`  | Те саме, що й для інших розкладів, з відповідним промптом |
| `get_celtic_cross_reading(question) -> (message_text, photo_paths, card_names)` | Тягне 10 **різних** карт (`get_random_unique_cards(10)`), будує один великий промпт з нумерованими позиціями `c1`..`c10`, повертає текст + 10 шляхів до фото + 10 назв у порядку позицій |

> ⚠️ **Чому порядок такий важливий:** і в `readings.py`, і в `handlers.py`
> фото й назви карт передаються як **паралельні списки** (`photo_paths`,
> `card_names`), що йдуть в одному й тому ж порядку, що й позиції
> (`THREE_CARDS_POSITIONS` / `CELTIC_CROSS_POSITIONS`). `zip()` у
> `handlers.py` покладається на це, щоб підписати кожне фото правильною
> позицією. Якщо колись знадобиться перемішати порядок показу — треба міняти
> порядок **самого списку позицій**, а не порядок виклику `get_something_for_card`.

---

## `src/handlers.py`

Єдиний `Router`, куди зареєстровані всі message- і callback-обробники.
Підключається до `Dispatcher` у `main.py` (`dp.include_router(router)`).

### Допоміжне

- `is_admin(user_id) -> bool` — `user_id == config.ADMIN_ID`. Використовується
  замість повторюваних `if X.from_user.id != ADMIN_ID` по всьому файлу.
- Константи цін: `READING_YES_NO_PRICE = 10.0`, `READING_THREE_CARDS_PRICE = 25.0`,
  `READING_CELTIC_CROSS_PRICE = 50.0`.
- Дані Mono-банки: `MONO_JAR_LINK`, `MONO_CARD`.

### FSM (StatesGroup)

| Група            | Стани | Призначення |
|------------------|-------|-------------|
| `SettingsStates` | `waiting_for_time` | Очікування вводу часу сповіщень |
| `AdminStates`    | `waiting_for_broadcast`, `waiting_for_payment_amount` | Розсилка й підтвердження Mono-оплати |
| `UserStates`     | `waiting_for_bug_report`, `waiting_for_stars_amount`, `waiting_for_mono_screenshot`, `waiting_for_yes_no_question`, `waiting_for_three_cards_question`, `waiting_for_celtic_cross_question` | Усі інші користувацькі очікування вводу |

### Групи обробників

**Головне меню** (`cmd_start`, `daily_card`, `reading_menu`, `setting`, `show_balance`)
— відповідають на текст reply-клавіатури (`F.text == "..."`) і показують
відповідні inline-клавіатури або одразу карту дня.

**Розклади** (`TAROT READINGS`) — по одному callback-обробнику `*_start` на
кожен розклад (перевіряє баланс → просить питання → ставить FSM-стан) і по
одному message-обробнику `process_*_question` на кожен стан (валідує
запит через Gemini → списує баланс → викликає відповідну функцію з
`readings.py` → надсилає альбом фото (`answer_media_group` з
`InputMediaPhoto`) → надсилає текст, розбиваючи на частини по 4000 символів,
якщо він довший за практичний ліміт Telegram).

**Налаштування** (`toggle_notify`, `ask_notify_time`, `save_notify_time`) —
зміна часу (з валідацією regex `([01]\d|2[0-3]):([0-5]\d)`) і toggle
сповіщень.

**Баланс і оплати**:
- `topup_mono` / `process_mono_screenshot` — просить скріншот, пересилає
  адміну з кнопкою підтвердження.
- `topup_stars_select` / `process_stars_amount` / `successful_payment` —
  реальний Telegram Stars інвойс (валюта `XTR`), нарахування балансу після
  `successful_payment` (курс 1 ⭐ = 1 ₴, зашито в тексті й у сумі інвойсу).
- `approve_mono_payment` / `process_payment_amount` — адмінський флоу
  підтвердження Mono-платежу вручну (адмін вводить суму → нараховується
  користувачу).

**Адмінка** (`admin_panel`, `admin_stats`, `admin_users_list`,
`admin_broadcast` / `process_broadcast` / `cancel_broadcast`) — доступно
лише `is_admin()`. Розсилка оновлює прогрес кожні 10 користувачів і має
кнопку скасування (стан скасування зберігається в `FSMContext`, а не в
глобальній змінній — тому воно per-conversation, а не глобальне на весь бот).

**Баг-репорти** (`report_bug` / `process_bug_report`) — пересилає текст
адміну з ID та юзернеймом.

---

## `src/main.py`

Точка входу.

1. `sys.path.insert(0, .../src)` — дозволяє запускати `python src/main.py`
   з кореня проєкту без встановлення пакету.
2. Створює `Bot`, кладе його в `config.BOT` (щоб інші модулі могли
   надсилати повідомлення поза контекстом `Message`/`CallbackQuery`).
3. `Dispatcher` + `dp.include_router(router)` з `handlers.py`.
4. `AsyncIOScheduler` (timezone `Europe/Kyiv`) з двома job'ами:
   - `database.reset_daily_cards` — щодня о 00:00.
   - `send_daily_notifications` — **щохвилини** (`cron minute="*"`):
     бере поточний час `HH:MM`, знаходить усіх, у кого `notify_time`
     збігається і `notify_enabled=1`, і надсилає їм карту дня через
     `day_card.send_daily_card_notification`.
5. `main()`: `database.init_db()` → `scheduler.start()` →
   `dp.start_polling(bot)`.

> ⚠️ Job щохвилини перевіряє **всіх** користувачів запитом до БД — прийнятно
> для невеликої/середньої кількості користувачів, але при масштабуванні до
> десятків тисяч користувачів варто розглянути індекс на `(notify_enabled, notify_time)`
> (SQLite і так швидко сканує невеликі таблиці, тому наразі це не проблема).

---

## Повні сценарії (флоу)

### Карта дня

```
Користувач → "🃏 Карта дня"
  → day_card.get_day_card_for_user(user_id)
      → читає today_give_card з БД
      → якщо NULL: tarrot_data.get_random_card() + database.set_today_card(...)
      → gemini_client.generate_text(PROMPT_TEMPLATE з картою)
  → бот надсилає фото карти, потім текст
```

Повторний виклик того самого дня поверне ту саму карту (бо `today_give_card`
вже заповнений) — новий текст-інтерпретація згенерується заново (текст не
кешується, лише сама карта).

### Так / Ні (10 ₴)

```
"🔮 Розклад" → "☯️ Так / Ні"
  → перевірка балансу (≥10₴), інакше show_alert і стоп
  → бот просить питання, стан = waiting_for_yes_no_question
Користувач пише питання
  → readings.is_yes_no_question(question)   [Gemini: ТАК/НІ]
  → якщо НІ: просить переформулювати, гроші НЕ списуються, стан лишається
  → якщо ТАК: database.add_balance(-10)
      → readings.get_yes_no_reading(question)
          → 1 випадкова карта, Gemini генерує "ТАК/НІ — пояснення"
      → бот надсилає фото карти, потім текст
      → стан очищується
```

### Розклад на 3 карти (25 ₴)

Той самий принцип, але:
- перевірка запиту ширша (не тільки так/ні-питання, а будь-яка життєва тема);
- тягнуться 3 **різні** карти в порядку минуле→теперішнє→майбутнє;
- бот спершу надсилає **альбом з 3 фото** (кожне підписане позицією й назвою
  карти), потім єдиний текст-розпис від Gemini.

### Кельтський Хрест (50 ₴)

Той самий принцип, у макс. масштабі:
- тягнуться 10 **різних** карт строго в порядку 10 позицій класичного
  розкладу;
- один великий промпт з усіма 10 картами одразу;
- бот надсилає **альбом рівно з 10 фото** (максимум, який Telegram дозволяє
  в одному медіа-альбомі), потім розгорнутий текст (розбивається на частини
  по 4000 символів, якщо потрібно).

### Автоматичні сповіщення

```
Щохвилини (APScheduler):
  current_time = HH:MM
  users = database.get_users_by_notify_time(current_time)  # notify_enabled=1 AND notify_time=current_time
  для кожного user_id: day_card.send_daily_card_notification(bot, user_id)
      (та сама логіка, що й ручна "Карта дня", але напряму через bot.send_*)

Щодня о 00:00:
  database.reset_daily_cards()  # today_give_card=NULL, day_card_mes=0 для всіх
```

### Поповнення балансу

**Mono**: користувач сам переказує довільну суму на банку/картку →
надсилає боту скріншот → бот пересилає скріншот адміну з кнопкою
"✅ Зарахувати баланс" → адмін тисне кнопку → вводить суму → бот нараховує
`database.add_balance` і повідомляє користувача.

**Telegram Stars**: користувач вводить кількість зірок → бот надсилає
реальний `send_invoice` (валюта `XTR`) → після оплати Telegram надсилає
`successful_payment` → бот парсить `payload` (`stars_{stars}_{user_id}`),
звіряє `user_id` і нараховує баланс 1:1 (1 ⭐ = 1 ₴).

---

## FSM-стани — зведена таблиця

| Стан (`StatesGroup.state`)                              | Встановлюється в           | Обробляється в                    |
|-----------------------------------------------------------|-----------------------------|-------------------------------------|
| `SettingsStates.waiting_for_time`                        | `ask_notify_time`           | `save_notify_time`                  |
| `AdminStates.waiting_for_broadcast`                      | `admin_broadcast`           | `process_broadcast`                 |
| `AdminStates.waiting_for_payment_amount`                 | `approve_mono_payment`      | `process_payment_amount`            |
| `UserStates.waiting_for_bug_report`                      | `report_bug`                | `process_bug_report`                |
| `UserStates.waiting_for_stars_amount`                    | `topup_stars_select`        | `process_stars_amount`              |
| `UserStates.waiting_for_mono_screenshot`                 | `topup_mono`                | `process_mono_screenshot`           |
| `UserStates.waiting_for_yes_no_question`                 | `reading_yes_no_start`       | `process_yes_no_question`           |
| `UserStates.waiting_for_three_cards_question`            | `reading_three_cards_start`  | `process_three_cards_question`      |
| `UserStates.waiting_for_celtic_cross_question`           | `reading_celtic_cross_start` | `process_celtic_cross_question`     |

## Callback-дані — зведена таблиця

| `callback_data`                  | Обробник                  | Хто може викликати |
|-----------------------------------|----------------------------|---------------------|
| `toggle_notify`                  | `toggle_notify`             | будь-хто |
| `set_notify_time`                | `ask_notify_time`            | будь-хто |
| `report_bug`                     | `report_bug`                 | будь-хто |
| `topup_mono`                     | `topup_mono`                 | будь-хто |
| `topup_stars_select`             | `topup_stars_select`         | будь-хто |
| `reading_yes_no`                 | `reading_yes_no_start`       | будь-хто (з перевіркою балансу) |
| `reading_three_cards`            | `reading_three_cards_start`  | будь-хто (з перевіркою балансу) |
| `reading_celtic_cross`           | `reading_celtic_cross_start` | будь-хто (з перевіркою балансу) |
| `admin_stats`                    | `admin_stats`                | тільки `ADMIN_ID` |
| `admin_users_list`               | `admin_users_list`           | тільки `ADMIN_ID` |
| `admin_broadcast`                | `admin_broadcast`            | тільки `ADMIN_ID` |
| `cancel_broadcast`               | `cancel_broadcast`           | тільки `ADMIN_ID` |
| `approve_mono_{user_id}`         | `approve_mono_payment`       | тільки `ADMIN_ID` (перевіряється всередині обробника) |

---

## Відомі обмеження та ідеї на майбутнє

- `read_all_users`, `set_day_card_true`, `delete_user` у `database.py` —
  публічні утиліти, які наразі ніде не викликаються з `handlers.py`.
  Залишені як готове API на майбутнє (напр. команда видалення акаунта).
- Ціна Кельтського Хреста (50 ₴) і 3-каркового розкладу (25 ₴) — orієнтовні
  значення, змінюються однією константою у верхній частині `handlers.py`.
- Rate limiter у `gemini_client.py` — process-local (не переживає рестарт і
  не ділиться між кількома інстансами бота, якщо колись буде горизонтальне
  масштабування).
- Немає механізму повторної спроби (retry) при падінні виклику Gemini —
  помилка спливе як виключення в обробнику; варто додати `try/except` з
  дружнім повідомленням користувачу за потреби.
- Media group у Telegram обмежена 10 елементами — Кельтський Хрест
  використовує рівно цей ліміт; додавання розкладу з більшою кількістю
  позицій вимагатиме розбиття на кілька альбомів.
