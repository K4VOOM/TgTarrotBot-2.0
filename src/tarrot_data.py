import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_PATH = PROJECT_ROOT / "assets"

tarrot_desk = {
    # --- СТАРШІ АРКАНИ (Major Arcana) ---
    "the_fool": {
        "name": "Блазень",
        "description": (
            "0. Блазень. Карта позначає безтурботність, легковажність, натхнення, творчість. "
            "Наприклад, вона може вказати, що вирішення майбутнього питання може вимагати творчого підходу."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_fool.jpg"
    },
    "the_magician": {
        "name": "Маг",
        "description": (
            "1. Маг. Символізує сильну і впевнену в собі людину, яка має можливість реалізувати свої плани. "
            "Цей Аркан позначає енергію, волю, готовність до рішучих дій, дипломатію."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_magician.jpg"
    },
    "the_high_priestess": {
        "name": "Верховна жриця",
        "description": (
            "2. Верховна жриця. Це мудрість, таємниці та екстрасенсорні здібності. Карта може "
            "уособлювати дівчину або жінку в оточені того, кому гадають. Жриця може вказувати "
            "на прихований талант, який може скоро проявитись."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_high_priestess.jpg"
    },
    "the_empress": {
        "name": "Імператриця",
        "description": (
            "3. Імператриця. Уособлює гармонію, процвітання та зростання. В будь-якому розкладі "
            "в can символізує стабільність та позитивний розвиток подій."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_empress.jpg"
    },
    "the_emperor": {
        "name": "Імператор",
        "description": (
            "4. Імператор. Позначає владу, авторитет і захист. Карта свідчить, що у того, кому "
            "гадають, є надійний захисник або ж він його потребує. Аркан Імператор, як "
            "характеристика особистості, означає, людина і є захисник."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_emperor.jpg"
    },
    "the_hierophant": {
        "name": "Ієрофант",
        "description": (
            "5. Ієрофант. Карта має багато значень, але в першу чергу цей аркан – протилежність "
            "Верховній Жриці. Позначає поневолення або необхідність отримання знань, процес "
            "навчання, а також недоліки."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_hierophant.jpg"
    },
    "the_lovers": {
        "name": "Закохані",
        "description": (
            "6. Закохані. Близькі стосунки, дружба, любов (іноді до себе). А також насолода, "
            "краса, спокуса, стабільність, союз, успіх. Наприклад, в розкладі на майбутнє "
            "карта може означати, що людина перебуває в гармонії з собою."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_lovers.jpg"
    },
    "the_chariot": {
        "name": "Колісниця",
        "description": (
            "7. Колісниця. Занепокоєння, поразка. Цей Аркан позначає саме дію, а не результат. "
            "Якщо в розкладі випадає колісниця, то прийшов час обдуманих вчинків."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_chariot.jpg"
    },
    "strength": {
        "name": "Сила",
        "description": (
            "8. Сила. Сила, влада, могутність, дія. Сила завжди означає необхідність діяти і, "
            "що, як колись більше не буде."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/strength.jpg"
    },
    "the_hermit": {
        "name": "Відлюдник",
        "description": (
            "9. Відлюдник. Терпіння, необхідність почекати, ізольованість. Аркан вказує на "
            "спад активності та уповільнення."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_hermit.jpg"
    },
    "wheel_of_fortune": {
        "name": "Фортуна",
        "description": (
            "10. Фортуна. Карта може мати різні значення, в залежності від карт, які "
            "лежать поряд. Найчастіше Фортуна означає: подарунок згори, успіх, зміни, "
            "різкий поворот долі."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/wheel_of_fortune.jpg"
    },
    "justice": {
        "name": "Справедливість",
        "description": "11. Справедливість. Карта балансу та обдуманих рішень, іноді, судових справ.",
        "classic_photo": "card_photo/classic/Major_Arcana/justice.jpg"
    },
    "the_hanged_man": {
        "name": "Повішений",
        "description": (
            "12. Повішений. Позначає інтуїцію, випробування, самопожертву, відмову від чогось. "
            "А також безперспективне майбутнє, важку роботу та рамки, яких доведеться дотримуватись."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_hanged_man.jpg"
    },
    "death": {
        "name": "Смерть",
        "description": (
            "13. Смерть. Означає кінець якогось періоду життя, в тому числі закінчення "
            "чорної смуги. А також може позначати втрату і розлуку."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/death.jpg"
    },
    "temperance": {
        "name": "Помірність",
        "description": (
            "14. Помірність. Необхідність знайти золоту середину в ситуації та балансувати "
            "між рішеннями."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/temperance.jpg"
    },
    "the_devil": {
        "name": "Диявол",
        "description": (
            "15. Диявол. Позначає жадібність, пристрасть, нездатність зупинитися, відчуття "
            "провини та незбалансованість."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_devil.jpg"
    },
    "the_tower": {
        "name": "Вежа",
        "description": (
            "16. Вежа. Великі зміни у житті, можуть бути, як хорошими, так і поганими – це "
            "залежить від карт, що розташовані поряд."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_tower.jpg"
    },
    "the_star": {
        "name": "Зірка",
        "description": "17. Зірка. Спокій, хороші новини, буденність. Хороший знак для запланованих дій.",
        "classic_photo": "card_photo/classic/Major_Arcana/the_star.jpg"
    },
    "the_moon": {
        "name": "Місяць",
        "description": (
            "18. Місяць. Самотність, втрата контролю. Місяць – це порада тому, кому гадають, "
            "що пора переосмислити своє життя."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_moon.jpg"
    },
    "the_sun": {
        "name": "Сонце",
        "description": (
            "19. Сонце. Символізує славу, успіх і визнання. В любовних гаданнях означає "
            "пристрасть і хіть."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_sun.jpg"
    },
    "judgement": {
        "name": "Суд",
        "description": (
            "20. Суд. Означає нові несподівані події, нагороди або покарання, занепокоєння. "
            "Дивлячись на розклад, може означати сильне почуття страху і тривоги."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/judgement.jpg"
    },
    "the_world": {
        "name": "Мир",
        "description": (
            "21. Мир. Остання карта в колоді старших арканів. Уособлює завершення чогось, "
            "подорож, а можливо втеча від самого себе."
        ),
        "classic_photo": "card_photo/classic/Major_Arcana/the_world.jpg"
    },

    # --- МОЛОДШІ АРКАНИ: КУБКИ (Minor Arcana: Cups) ---
    "ace_of_cups": {
        "name": "Туз Кубків",
        "description": (
            "Туз Кубків. Стихія – вода. Символізують спокій, усамітнення, відносини з "
            "оточуючими, любовні переживання. Пряме положення: кохання, творчість, емоційне пробудження."
        ),
        "classic_photo": "card_photo/classic/Cups/ace_of_cups.jpg"
    },
    "two_of_cups": {
        "name": "Двійка Кубків",
        "description": "Двійка Кубків. Пряме положення: єдність, партнерство, зв’язок.",
        "classic_photo": "card_photo/classic/Cups/two_of_cups.jpg"
    },
    "three_of_cups": {
        "name": "Трійка Кубків",
        "description": "Трійка Кубків. Пряме положення: дружба, однодумці.",
        "classic_photo": "card_photo/classic/Cups/three_of_cups.jpg"
    },
    "four_of_cups": {
        "name": "Четвірка Кубків",
        "description": "Четвірка Кубків. Пряме положення: апатія, меланхолія, нудьга.",
        "classic_photo": "card_photo/classic/Cups/four_of_cups.jpg"
    },
    "five_of_cups": {
        "name": "П’ятірка Кубків",
        "description": "П’ятірка Кубків. Пряме положення: втрата, розчарування, смуток.",
        "classic_photo": "card_photo/classic/Cups/five_of_cups.jpg"
    },
    "six_of_cups": {
        "name": "Шістка Кубків",
        "description": "Шістка Кубків. Пряме положення: ностальгія, спогади, лікування.",
        "classic_photo": "card_photo/classic/Cups/six_of_cups.jpg"
    },
    "seven_of_cups": {
        "name": "Сімка Кубків",
        "description": "Сімка Кубків. Пряме положення: вибір, пошук мети, ілюзія.",
        "classic_photo": "card_photo/classic/Cups/seven_of_cups.jpg"
    },
    "eight_of_cups": {
        "name": "Вісімка Кубків",
        "description": "Вісімка Кубків. Пряме положення: відпустити ситуацію, піти від чогось/когось.",
        "classic_photo": "card_photo/classic/Cups/eight_of_cups.jpg"
    },
    "nine_of_cups": {
        "name": "Дев’ятка Кубків",
        "description": "Дев’ятка Кубків. Пряме положення: виконання бажань, задоволення, достаток.",
        "classic_photo": "card_photo/classic/Cups/nine_of_cups.jpg"
    },
    "ten_of_cups": {
        "name": "Десятка Кубків",
        "description": (
            "Десятка Кубків. Пряме положення: щастя, повернення додому, емоційна "
            "стабільність, самореалізація."
        ),
        "classic_photo": "card_photo/classic/Cups/ten_of_cups.jpg"
    },
    "page_of_cups": {
        "name": "Паж Кубків",
        "description": "Паж Кубків. Пряме положення: ідеалізм, наївність, чутливість.",
        "classic_photo": "card_photo/classic/Cups/page_of_cups.jpg"
    },
    "knight_of_cups": {
        "name": "Лицар Кубків",
        "description": "Лицар Кубків. Пряме положення: артистичність, граційність, ідеалізм.",
        "classic_photo": "card_photo/classic/Cups/knight_of_cups.jpg"
    },
    "queen_of_cups": {
        "name": "Королева Кубків",
        "description": "Королева Кубків. Пряме положення: співчуття, доброта, інтуїція.",
        "classic_photo": "card_photo/classic/Cups/queen_of_cups.jpg"
    },
    "king_of_cups": {
        "name": "Король Кубків",
        "description": (
            "Король Кубків. Пряме положення: мудрість, дипломатичність, баланс між "
            "емоціями і логікою, відданість."
        ),
        "classic_photo": "card_photo/classic/Cups/king_of_cups.jpg"
    },

    # --- МОЛОДШІ АРКАНИ: ЖЕЗЛИ (Minor Arcana: Wands) ---
    "ace_of_wands": {
        "name": "Туз Жезлів",
        "description": (
            "Туз Жезлів. Стихія – вогонь. Символізують енергію, життєву силу і амбіції. "
            "Найчастіше вказують на роботу, бізнес і результат. Пряме положення: удача, успіх, кар’єрний ріст, натхнення."
        ),
        "classic_photo": "card_photo/classic/Wands/ace_of_wands.jpg"
    },
    "two_of_wands": {
        "name": "Двійка Жезлів",
        "description": "Двійка Жезлів. Пряме положення: планування, прийняття рішень.",
        "classic_photo": "card_photo/classic/Wands/two_of_wands.jpg"
    },
    "three_of_wands": {
        "name": "Трійка Жезлів",
        "description": (
            "Трійка Жезлів. Особа досягає всього в житті самостійно (якщо 3+ карт масті). "
            "Пряме положення: впевненість, зростання."
        ),
        "classic_photo": "card_photo/classic/Wands/three_of_wands.jpg"
    },
    "four_of_wands": {
        "name": "Четвірка Жезлів",
        "description": "Четвірка Жезлів. Пряме положення: зустріч, свято, спільнота.",
        "classic_photo": "card_photo/classic/Wands/four_of_wands.jpg"
    },
    "five_of_wands": {
        "name": "П’ятірка Жезлів",
        "description": "П’ятірка Жезлів. Пряме положення: конфлікт, конкуренція.",
        "classic_photo": "card_photo/classic/Wands/five_of_wands.jpg"
    },
    "six_of_wands": {
        "name": "Шістка Жезлів",
        "description": "Шістка Жезлів. Пряме положення: успіх, перемога, винагорода.",
        "classic_photo": "card_photo/classic/Wands/six_of_wands.jpg"
    },
    "seven_of_wands": {
        "name": "Сімка Жезлів",
        "description": "Сімка Жезлів. Пряме положення: захист, відстоювання інтересів та простору.",
        "classic_photo": "card_photo/classic/Wands/seven_of_wands.jpg"
    },
    "eight_of_wands": {
        "name": "Вісімка Жезлів",
        "description": "Вісімка Жезлів. Пряме положення: прогрес, активність, швидке рішення.",
        "classic_photo": "card_photo/classic/Wands/eight_of_wands.jpg"
    },
    "nine_of_wands": {
        "name": "Дев’ятка Жезлів",
        "description": "Дев’ятка Жезлів. Пряме положення: останній бій, наполегливість.",
        "classic_photo": "card_photo/classic/Wands/nine_of_wands.jpg"
    },
    "ten_of_wands": {
        "name": "Десятка Жезлів",
        "description": "Десятка Жезлів. Пряме положення: тягар, відповідальність, борг, стрес.",
        "classic_photo": "card_photo/classic/Wands/ten_of_wands.jpg"
    },
    "page_of_wands": {
        "name": "Паж Жезлів",
        "description": "Паж Жезлів. Пряме положення: пригоди, азарт, ідеї.",
        "classic_photo": "card_photo/classic/Wands/page_of_wands.jpg"
    },
    "knight_of_wands": {
        "name": "Лицар Жезлів",
        "description": "Лицар Жезлів. Пряме положення: мужність, енергійність, привабливість.",
        "classic_photo": "card_photo/classic/Wands/knight_of_wands.jpg"
    },
    "queen_of_wands": {
        "name": "Королева Жезлів",
        "description": "Королева Жезлів. Пряме положення: впевненість у собі, рішучість.",
        "classic_photo": "card_photo/classic/Wands/queen_of_wands.jpg"
    },
    "king_of_wands": {
        "name": "Король Жезлів",
        "description": "Король Жезлів. Пряме положення: лідерство, ухвалення рішень.",
        "classic_photo": "card_photo/classic/Wands/king_of_wands.jpg"
    },

    # --- МОЛОДШІ АРКАНИ: МЕЧІ (Minor Arcana: Swords) ---
    "ace_of_swords": {
        "name": "Туз Мечів",
        "description": (
            "Туз Мечів. Стихія – повітря. Символізують духовні блага, приховані сфери, почуття "
            "та емоції. Найнебезпечніша масть. Пряме положення: ясність, інсайд, концентрація."
        ),
        "classic_photo": "card_photo/classic/Swords/ace_of_swords.jpg"
    },
    "two_of_swords": {
        "name": "Двійка Мечів",
        "description": "Двійка Мечів. Пряме положення: глухий кут, важкий вибір, заперечення.",
        "classic_photo": "card_photo/classic/Swords/two_of_swords.jpg"
    },
    "three_of_swords": {
        "name": "Трійка Мечів",
        "description": "Трійка Мечів. Пряме положення: розбите серце, сум, горе.",
        "classic_photo": "card_photo/classic/Swords/three_of_swords.jpg"
    },
    "four_of_swords": {
        "name": "Четвірка Мечів",
        "description": "Четвірка Мечів. Пряме положення: відпочинок, спокій, притулок.",
        "classic_photo": "card_photo/classic/Swords/four_of_swords.jpg"
    },
    "five_of_swords": {
        "name": "П’ятірка Мечів",
        "description": "П’ятірка Мечів. Пряме положення: суперечки, залякування, агресія, аргументи.",
        "classic_photo": "card_photo/classic/Swords/five_of_swords.jpg"
    },
    "six_of_swords": {
        "name": "Шістка Мечів",
        "description": "Шістка Мечів. Пряме положення: рух вперед, залишення позаду.",
        "classic_photo": "card_photo/classic/Swords/six_of_swords.jpg"
    },
    "seven_of_swords": {
        "name": "Сімка Мечів",
        "description": "Сімка Мечів. Пряме положення: брехня, хитрість, інтрига, нечесна гра.",
        "classic_photo": "card_photo/classic/Swords/seven_of_swords.jpg"
    },
    "eight_of_swords": {
        "name": "Вісімка Мечів",
        "description": "Вісімка Мечів. Пряме положення: обмеження, відчуття, як у пастці.",
        "classic_photo": "card_photo/classic/Swords/eight_of_swords.jpg"
    },
    "nine_of_swords": {
        "name": "Дев’ятка Мечів",
        "description": "Дев’ятка Мечів. Пряме положення: страх, негативність, переломний момент.",
        "classic_photo": "card_photo/classic/Swords/nine_of_swords.jpg"
    },
    "ten_of_swords": {
        "name": "Десятка Мечів",
        "description": "Десятка Мечів. Пряме положення: гірка печаль, руйнація, невдача.",
        "classic_photo": "card_photo/classic/Swords/ten_of_swords.jpg"
    },
    "page_of_swords": {
        "name": "Паж Мечів",
        "description": "Паж Мечів. Пряме положення: допитливість, дотепність, комунікабельність.",
        "classic_photo": "card_photo/classic/Swords/page_of_swords.jpg"
    },
    "knight_of_swords": {
        "name": "Лицар Мечів",
        "description": "Лицар Мечів. Пряме положення: наполегливість, прямота, інтелект.",
        "classic_photo": "card_photo/classic/Swords/knight_of_swords.jpg"
    },
    "queen_of_swords": {
        "name": "Королева Мечів",
        "description": (
            "Королева Мечів. Пряме положення: незалежність, справедливість, важливість, чесноти."
        ),
        "classic_photo": "card_photo/classic/Swords/queen_of_swords.jpg"
    },
    "king_of_swords": {
        "name": "Король Мечів",
        "description": "Король Мечів. Пряме положення: розум, дисципліна, чесність.",
        "classic_photo": "card_photo/classic/Swords/king_of_swords.jpg"
    },

    # --- МОЛОДШІ АРКАНИ: ПЕНТАКЛІ (Minor Arcana: Pentacles) ---
    "ace_of_pentacles": {
        "name": "Туз Пентаклів",
        "description": (
            "Туз Пентаклів. Стихія – земля. Масть відповідає за фінансову сферу, прибуток, "
            "достаток або втрати. Пряме положення: ресурси, нові можливості, процвітання."
        ),
        "classic_photo": "card_photo/classic/Pentacles/ace_of_pentacles.jpg"
    },
    "two_of_pentacles": {
        "name": "Двійка Пентаклів",
        "description": "Двійка Пентаклів. Пряме положення: баланс ресурсів, винахідливість, гнучкість, адаптація.",
        "classic_photo": "card_photo/classic/Pentacles/two_of_pentacles.jpg"
    },
    "three_of_pentacles": {
        "name": "Трійка Пентаклів",
        "description": "Трійка Пентаклів. Пряме положення: командна робота, спільні цілі.",
        "classic_photo": "card_photo/classic/Pentacles/three_of_pentacles.jpg"
    },
    "four_of_pentacles": {
        "name": "Четвірка Пентаклів",
        "description": "Четвірка Пентаклів. Пряме положення: власництво, накопичення, скупість.",
        "classic_photo": "card_photo/classic/Pentacles/four_of_pentacles.jpg"
    },
    "five_of_pentacles": {
        "name": "П’ятірка Пентаклів",
        "description": "П’ятірка Пентаклів. Пряме положення: втрата, проблеми, відчуття покинутості.",
        "classic_photo": "card_photo/classic/Pentacles/five_of_pentacles.jpg"
    },
    "six_of_pentacles": {
        "name": "Шістка Пентаклів",
        "description": "Шістка Пентаклів. Пряме положення: щедрість, благодійність, матеріальна допомога.",
        "classic_photo": "card_photo/classic/Pentacles/six_of_pentacles.jpg"
    },
    "seven_of_pentacles": {
        "name": "Сімка Пентаклів",
        "description": "Сімка Пентаклів. Пряме положення: урожай, винагорода, ріст.",
        "classic_photo": "card_photo/classic/Pentacles/seven_of_pentacles.jpg"
    },
    "eight_of_pentacles": {
        "name": "Вісімка Пентаклів",
        "description": "Вісімка Пентаклів. Пряме положення: вміння, талант, майстерність, якість.",
        "classic_photo": "card_photo/classic/Pentacles/eight_of_pentacles.jpg"
    },
    "nine_of_pentacles": {
        "name": "Дев’ятка Пентаклів",
        "description": "Дев’ятка Пентаклів. Пряме положення: винагорода за зусилля, здобутки, незалежність.",
        "classic_photo": "card_photo/classic/Pentacles/nine_of_pentacles.jpg"
    },
    "ten_of_pentacles": {
        "name": "Десятка Пентаклів",
        "description": "Десятка Пентаклів. Пряме положення: сім’я, спадщина.",
        "classic_photo": "card_photo/classic/Pentacles/ten_of_pentacles.jpg"
    },
    "page_of_pentacles": {
        "name": "Паж Пентаклів",
        "description": "Паж Пентаклів. Пряме положення: амбітність, старанність, цілеспрямованість.",
        "classic_photo": "card_photo/classic/Pentacles/page_of_pentacles.jpg"
    },
    "knight_of_pentacles": {
        "name": "Лицар Пентаклів",
        "description": "Лицар Пентаклів. Пряме положення: працьовитість, терплячість, ефективність та надійність.",
        "classic_photo": "card_photo/classic/Pentacles/knight_of_pentacles.jpg"
    },
    "queen_of_pentacles": {
        "name": "Королева Пентаклів",
        "description": "Королева Пентаклів. Пряме положення: щедрість, вихованість, гостинність, час вдома.",
        "classic_photo": "card_photo/classic/Pentacles/queen_of_pentacles.jpg"
    },
    "king_of_pentacles": {
        "name": "Король Пентаклів",
        "description": "Король Пентаклів. Пряме положення: достаток та процвітання, безпека, амбіції.",
        "classic_photo": "card_photo/classic/Pentacles/king_of_pentacles.jpg"
    }
}

def get_random_card():
        return random.choice(list(tarrot_desk.items()))[0]

def get_something_for_card(system_name: str, something: str):
    value = tarrot_desk[system_name][something]
    if something == "classic_photo" and isinstance(value, str):
        return str(ASSETS_PATH / value)
    return value