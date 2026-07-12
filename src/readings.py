import gemini_client
import tarrot_data

# ===== ТАК / НІ =====

YES_NO_CLASSIFY_PROMPT_TEMPLATE = """\
Ти — помічник Таро-бота. Тобі дається питання від користувача.

Питання: "{question}"

Визнач, чи є це питання закритим і придатним для відповіді у форматі
"так/ні" (наприклад: "Чи варто мені змінити роботу?", "Чи повернеться він?").
Питання НЕ підходить, якщо воно відкрите, потребує розгорнутої відповіді,
просить пораду "як зробити щось", або взагалі не є питанням
(наприклад: "Що мені робити далі?", "Розкажи про мій день").

Відповідай СТРОГО одним словом, без пояснень і розділових знаків:
ТАК — якщо питання підходить для формату так/ні
НІ — якщо не підходить
"""

YES_NO_ANSWER_PROMPT_TEMPLATE = """\
Ти — таролог, який дає коротку відповідь у форматі "так/ні" на питання
користувача, спираючись на випадково витягнуту карту Таро. Пиши українською,
спокійним і впевненим тоном (на "ти"), без зайвого пафосу та жартів.

Питання: "{question}"
Карта: {card_name}
Опис карти: {card_description}

Виходячи зі значення карти в контексті цього питання, обери ОДНУ відповідь —
ТАК або НІ — і додай коротке (до 15 слів) пояснення без вступних слів.

Формат відповіді СТРОГО (одним рядком, без лапок і зайвого форматування):
ТАК — [коротке пояснення]
або
НІ — [коротке пояснення]
"""


async def is_yes_no_question(question: str) -> bool:
    """Питає Gemini, чи можна відповісти на питання у форматі так/ні."""
    prompt = YES_NO_CLASSIFY_PROMPT_TEMPLATE.format(question=question)
    answer = await gemini_client.generate_text(prompt)
    return answer.strip().upper().startswith("ТАК")


async def generate_yes_no_answer(card_name: str, card_description: str, question: str) -> str:
    """Повертає рядок виду 'ТАК — пояснення' або 'НІ — пояснення'."""
    prompt = YES_NO_ANSWER_PROMPT_TEMPLATE.format(
        question=question,
        card_name=card_name,
        card_description=card_description,
    )
    return await gemini_client.generate_text(prompt)


async def get_yes_no_reading(question: str) -> tuple[str, str]:
    """
    Повний сценарій розкладу 'Так/Ні': тягне випадкову карту (так само,
    як і карта дня) і повертає (message_text, photo_path):

    🔮 Ваше питання: ...

    🃏 Карта відповіді:
    ТАК — ...
    """
    system_name = tarrot_data.get_random_card()
    card_name = tarrot_data.get_something_for_card(system_name, "name")
    card_description = tarrot_data.get_something_for_card(system_name, "description")
    photo_path = tarrot_data.get_something_for_card(system_name, "classic_photo")

    answer_line = await generate_yes_no_answer(card_name, card_description, question)

    message_text = (
        f"🔮 Ваше питання: {question}\n\n"
        f"🃏 Карта відповіді:\n"
        f"{answer_line}"
    )
    return message_text, photo_path


# ===== РОЗКЛАД НА 3 КАРТИ (Минуле — Теперішнє — Майбутнє) =====

THREE_CARDS_POSITIONS = [
    ("🕰 Минуле", "past"),
    ("✨ Теперішнє", "present"),
    ("🔮 Майбутнє", "future"),
]

THREE_CARDS_CLASSIFY_PROMPT_TEMPLATE = """\
Ти — помічник Таро-бота. Тобі дається запит від користувача для розкладу
"Минуле-Теперішнє-Майбутнє".

Запит: "{question}"

Визнач, чи це осмислений запит/питання про ситуацію в житті користувача,
на яке можна дати розгорнуту відповідь через призму минулого, теперішнього
і майбутнього (наприклад: "Як складуться мої стосунки?", "Що чекає на мене
у кар'єрі?", "Розкажи про мій фінансовий стан").

Запит НЕ підходить, якщо це порожній текст, беззмістовний набір символів,
команда боту, образа, чи запит, що не стосується життєвої ситуації.

Відповідай СТРОГО одним словом, без пояснень і розділових знаків:
ТАК — якщо запит підходить для розкладу
НІ — якщо не підходить
"""

THREE_CARDS_ANSWER_PROMPT_TEMPLATE = """\
Ти — таролог, який робить розклад "Минуле-Теперішнє-Майбутнє" для
Telegram-бота. Пиши українською, спокійним і впевненим тоном (на "ти"),
без зайвого пафосу, жартів і вигаданих деталей про конкретну людину.

Запит користувача: "{question}"

Ось три витягнуті карти:

Минуле: {past_name} — {past_description}
Теперішнє: {present_name} — {present_description}
Майбутнє: {future_name} — {future_description}

Напиши повідомлення СТРОГО за такою структурою і форматом (заміни emoji
карти на найбільш підходящу за змістом карти для кожної позиції):

🕰 Минуле — {past_name}
[1-2 речення про те, як минуле вплинуло на поточну ситуацію]

✨ Теперішнє — {present_name}
[1-2 речення про поточний стан справ]

🔮 Майбутнє — {future_name}
[1-2 речення про ймовірний розвиток подій]

✨ Загальний висновок: [Одне-два речення підсумку і поради]

Не додавай нічого, крім цього повідомлення. Не використовуй markdown-розмітку
(зірочки, решітки тощо), лише emoji та звичайний текст.
"""


async def is_valid_three_cards_question(question: str) -> bool:
    """Питає Gemini, чи запит користувача осмислений і придатний для розкладу."""
    prompt = THREE_CARDS_CLASSIFY_PROMPT_TEMPLATE.format(question=question)
    answer = await gemini_client.generate_text(prompt)
    return answer.strip().upper().startswith("ТАК")


async def get_three_cards_reading(question: str) -> tuple[str, list[str], list[str]]:
    """
    Повний сценарій розкладу 'Минуле-Теперішнє-Майбутнє'.

    Тягне 3 РІЗНІ випадкові карти (без повторів) у порядку
    минуле -> теперішнє -> майбутнє і повертає:
    - message_text — фінальний текст-розпис від Gemini;
    - photo_paths — шляхи до фото карт у тому ж порядку (важлива черговість!);
    - card_names — назви карт у тому ж порядку (для підписів до фото).
    """
    system_names = tarrot_data.get_random_unique_cards(3)

    card_names = [tarrot_data.get_something_for_card(name, "name") for name in system_names]
    card_descriptions = [
        tarrot_data.get_something_for_card(name, "description") for name in system_names
    ]
    photo_paths = [
        tarrot_data.get_something_for_card(name, "classic_photo") for name in system_names
    ]

    prompt = THREE_CARDS_ANSWER_PROMPT_TEMPLATE.format(
        question=question,
        past_name=card_names[0],
        past_description=card_descriptions[0],
        present_name=card_names[1],
        present_description=card_descriptions[1],
        future_name=card_names[2],
        future_description=card_descriptions[2],
    )

    analysis_text = await gemini_client.generate_text(prompt)

    message_text = f"🔮 Ваше питання: {question}\n\n{analysis_text}"
    return message_text, photo_paths, card_names
