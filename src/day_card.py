from aiogram.types import FSInputFile

import database
import gemini_client
import tarrot_data

PROMPT_TEMPLATE = """\
Ти — таролог, який пише коротке щоденне послання "Карта дня" для Telegram-бота.
Пиши українською мовою, спокійним, стриманим і впевненим тоном (на "ти"),
без награного гумору, без зайвого пафосу та без вигаданих деталей про конкретну людину.

Ось карта дня:
Назва: {card_name}
Опис: {card_description}

Напиши повідомлення СТРОГО за такою структурою і форматом (заміни emoji карти
на найбільш підходящу за змістом карти, а текст під кожним пунктом — придумай
сам, спираючись на опис карти):

✨ Ваша поточна карта на сьогодні:
🃏 {card_name}

[Один короткий (1-2 речення) стриманий коментар до суті карти, без спроб пожартувати]

🌿 Здоров'я: [1-2 речення про стан здоров'я/енергії дня]
💰 Фінанси: [1-2 речення про фінанси дня]
❤️ Відносини: [1-2 речення про стосунки/спілкування дня]

✨ Афірмація дня: [Одне коротке речення-афірмація від першої особи]

Не додавай нічого, крім цього повідомлення. Не використовуй markdown-розмітку
(зірочки, решітки тощо), лише emoji та звичайний текст.
"""


async def generate_day_card_message(card_name: str, card_description: str) -> str:
    prompt = PROMPT_TEMPLATE.format(
        card_name=card_name,
        card_description=card_description,
    )
    return await gemini_client.generate_text(prompt)


async def get_day_card_for_user(user_id: int) -> tuple[str, str]:
    user_data = database.read_user(user_id)
    system_name = user_data[3]  # today_give_card

    if system_name is None:
        system_name = tarrot_data.get_random_card()
        database.set_today_card(user_id, system_name)

    card_name = tarrot_data.get_something_for_card(system_name, "name")
    card_description = tarrot_data.get_something_for_card(system_name, "description")
    photo_path = tarrot_data.get_something_for_card(system_name, "classic_photo")

    message_text = await generate_day_card_message(card_name, card_description)
    return message_text, photo_path


async def send_daily_card_notification(bot, user_id: int) -> bool:
    try:
        message_text, photo_path = await get_day_card_for_user(user_id)
        photo = FSInputFile(photo_path)
        await bot.send_photo(chat_id=user_id, photo=photo)
        await bot.send_message(chat_id=user_id, text=message_text)
        return True
    except Exception as e:
        print(f"❌ Помилка при відправці карти користувачу {user_id}: {e}")
        return False
