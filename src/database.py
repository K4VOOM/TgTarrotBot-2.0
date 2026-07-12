import sqlite3
from pathlib import Path

# Знайти корінь проекту та побудувати портативний шлях до БД
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "list_users.db"


def get_connection():
    return sqlite3.connect(str(DB_PATH))


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                day_card_mes INTEGER DEFAULT 0,
                today_give_card TEXT DEFAULT NULL,
                notify_time TEXT DEFAULT '09:00',
                notify_enabled INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
    print("БД успішно ініціалізована.")


def create_user(user_id: int, username: str):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Помилка при створенні запису: {e}")


def read_user(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, day_card_mes, today_give_card, notify_time, notify_enabled FROM users WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone()


def read_all_users():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()


def set_day_card_true(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET day_card_mes = 1 WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()


def delete_user(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()


def set_today_card(user_id: int, card_name: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET today_give_card = ? WHERE user_id = ?",
            (card_name, user_id)
        )
        conn.commit()


def reset_daily_cards():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET today_give_card = NULL, day_card_mes = 0"
        )
        conn.commit()
    print("Карти дня скинуто для всіх користувачів.")


def set_notify_time(user_id: int, time_str: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET notify_time = ? WHERE user_id = ?",
            (time_str, user_id)
        )
        conn.commit()


def toggle_notify_enabled(user_id: int) -> int:
    """Перемикає notify_enabled (0<->1) і повертає нове значення."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET notify_enabled = 1 - notify_enabled WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        cursor.execute(
            "SELECT notify_enabled FROM users WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone()[0]


def get_users_by_notify_time(notify_time: str):
    """Отримує всіх користувачів з увімкненими сповіщеннями на конкретний час."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM users WHERE notify_enabled = 1 AND notify_time = ?",
            (notify_time,)
        )
        return cursor.fetchall()