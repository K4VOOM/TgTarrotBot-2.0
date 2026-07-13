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


# ===== РОЗКЛАД "КЕЛЬТСЬКИЙ ХРЕСТ" (10 карт) =====

CELTIC_CROSS_POSITIONS = [
    ("1️⃣", "Поточна ситуація"),
    ("2️⃣", "Перешкода"),
    ("3️⃣", "Минуле"),
    ("4️⃣", "Найближче майбутнє"),
    ("5️⃣", "Свідоме"),
    ("6️⃣", "Підсвідоме"),
    ("7️⃣", "Сам кверент"),
    ("8️⃣", "Зовнішні впливи"),
    ("9️⃣", "Надії і страхи"),
    ("🔟", "Результат"),
]

CELTIC_CROSS_CLASSIFY_PROMPT_TEMPLATE = """\
Ти — помічник Таро-бота. Тобі дається запит від користувача для глибокого
аналітичного розкладу "Кельтський Хрест" (10 карт).

Запит: "{question}"

Визнач, чи це осмислений запит про життєву ситуацію (стосунки, кар'єра,
життєвий вибір, духовний шлях тощо), на яке можна дати розгорнутий
багатогранний аналіз (наприклад: "Що чекає на мої стосунки?",
"Чи варто мені змінювати роботу?", "Як розвиватиметься мій духовний шлях?").

Запит НЕ підходить, якщо це порожній текст, беззмістовний набір символів,
команда боту, образа, чи запит, що не стосується життєвої ситуації людини.

Відповідай СТРОГО одним словом, без пояснень і розділових знаків:
ТАК — якщо запит підходить для розкладу
НІ — якщо не підходить
"""

CELTIC_CROSS_ANSWER_PROMPT_TEMPLATE = """\
Ти — досвідчений таролог, який робить розклад "Кельтський Хрест" (10 карт)
для Telegram-бота. Пиши українською, спокійним і впевненим тоном (на "ти"),
без зайвого пафосу, жартів і вигаданих деталей про конкретну людину.

Запит користувача: "{question}"

Ось десять витягнутих карт по позиціях:

1️⃣ Поточна ситуація (серце запиту): {c1_name} — {c1_description}
2️⃣ Перешкода (що заважає): {c2_name} — {c2_description}
3️⃣ Минуле (коріння ситуації): {c3_name} — {c3_description}
4️⃣ Найближче майбутнє: {c4_name} — {c4_description}
5️⃣ Свідоме (те, що "над ним"): {c5_name} — {c5_description}
6️⃣ Підсвідоме (те, що "під ним"): {c6_name} — {c6_description}
7️⃣ Сам кверент (роль і стан): {c7_name} — {c7_description}
8️⃣ Зовнішні впливи (обставини й оточення): {c8_name} — {c8_description}
9️⃣ Надії і страхи (внутрішній конфлікт): {c9_name} — {c9_description}
🔟 Результат (можливий підсумок): {c10_name} — {c10_description}

Напиши повідомлення СТРОГО за такою структурою і форматом (заміни кожен
[коментар] на 1-2 речення власного тлумачення карти саме в контексті
запиту користувача, спираючись на позицію й опис карти):

1️⃣ Поточна ситуація — {c1_name}
[коментар]

2️⃣ Перешкода — {c2_name}
[коментар]

3️⃣ Минуле — {c3_name}
[коментар]

4️⃣ Найближче майбутнє — {c4_name}
[коментар]

5️⃣ Свідоме — {c5_name}
[коментар]

6️⃣ Підсвідоме — {c6_name}
[коментар]

7️⃣ Сам кверент — {c7_name}
[коментар]

8️⃣ Зовнішні впливи — {c8_name}
[коментар]

9️⃣ Надії і страхи — {c9_name}
[коментар]

🔟 Результат — {c10_name}
[коментар]

✨ Висновок: [2-3 речення загального підсумку по всьому розкладу]
👉 Порада: [1-2 речення конкретної поради кверенту]

Не додавай нічого, крім цього повідомлення. Не використовуй markdown-розмітку
(зірочки, решітки тощо), лише emoji та звичайний текст.
"""


async def is_valid_celtic_cross_question(question: str) -> bool:
    """Питає Gemini, чи запит користувача підходить для розкладу Кельтський Хрест."""
    prompt = CELTIC_CROSS_CLASSIFY_PROMPT_TEMPLATE.format(question=question)
    answer = await gemini_client.generate_text(prompt)
    return answer.strip().upper().startswith("ТАК")


async def get_celtic_cross_reading(question: str) -> tuple[str, list[str], list[str]]:
    """
    Повний сценарій розкладу 'Кельтський Хрест'.

    Тягне 10 РІЗНИХ випадкових карт (без повторів) у порядку позицій 1-10
    і повертає:
    - message_text — фінальний текст-розпис від Gemini (з усіма 10 позиціями,
      висновком і порадою);
    - photo_paths — шляхи до фото карт у порядку позицій (важлива черговість!);
    - card_names — назви карт у тому ж порядку (для підписів до фото).
    """
    system_names = tarrot_data.get_random_unique_cards(10)

    card_names = [tarrot_data.get_something_for_card(name, "name") for name in system_names]
    card_descriptions = [
        tarrot_data.get_something_for_card(name, "description") for name in system_names
    ]
    photo_paths = [
        tarrot_data.get_something_for_card(name, "classic_photo") for name in system_names
    ]

    prompt = CELTIC_CROSS_ANSWER_PROMPT_TEMPLATE.format(
        question=question,
        c1_name=card_names[0], c1_description=card_descriptions[0],
        c2_name=card_names[1], c2_description=card_descriptions[1],
        c3_name=card_names[2], c3_description=card_descriptions[2],
        c4_name=card_names[3], c4_description=card_descriptions[3],
        c5_name=card_names[4], c5_description=card_descriptions[4],
        c6_name=card_names[5], c6_description=card_descriptions[5],
        c7_name=card_names[6], c7_description=card_descriptions[6],
        c8_name=card_names[7], c8_description=card_descriptions[7],
        c9_name=card_names[8], c9_description=card_descriptions[8],
        c10_name=card_names[9], c10_description=card_descriptions[9],
    )

    analysis_text = await gemini_client.generate_text(prompt)

    message_text = f"🔮 Ваше питання: {question}\n\n{analysis_text}"
    return message_text, photo_paths, card_names
