import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================== ТОКЕН ==================
TOKEN = "8739520899:AAGJY_4dGtyUoHS80iK1uqXI29gLruGnTnQ"
BOT_NAME = "kaorii"

# ================== АДМИНЫ ==================
ADMIN_USERNAMES = ["fsvsf", "oncud"]  # Без @
ADMIN_IDS = []  # Заполнится при первом обращении

# ================== ХРАНИЛИЩА ==================
user_data = {}
marriages = {}
promocodes = {}  # {code: {reward_type, reward_amount, uses_left, created_by}}

# ================== ИНИЦИАЛИЗАЦИЯ ==================
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================== ХАРАКТЕР КАОРИ ==================
ANGRY_REPLIES = [
    "НУ ЧЁ НАДО? ОТЪЕБИСЬ! 😡",
    "ЗВАЛ? ЗАВАЛИ ЕБАЛО! 🤬",
    "ЧЁ ТЫ МЕНЯ ТРОГАЕШЬ? ЗАНЯТА Я! 🖕",
    "ОПЯТЬ ТЫ? ЧЁ ТЕБЕ НАДО, МЕЛОЧЬ?",
    "НУ? ГОВОРИ БЫСТРЕЕ, ПОКА Я ТЕБЕ НЕ ВПИСАЛА! 💀",
    "СЛУШАЮ. НО ЕСЛИ ХУЙНЮ СКАЖЕШЬ — ПОЖАЛЕЕШЬ!",
    "ДА-ДА, Я ТУТ. ЧЁ НАДО, СМЕРТНЫЙ?",
]

KAORI_INFO_TEMPLATES = [
    "📊 Инфа что {question} — {percent}%",
    "📊 Я ТУТ ПОДУМАЛА... {question} — ЭТО {percent}%",
    "📊 ПО ПРОГНОЗУ КАОРИ: {question} — {percent}%",
    "📊 МОЯ ОЦЕНКА: {question} — {percent}%, НЕ БОЛЬШЕ!",
]

BOOBS_MESSAGES = [
    "🍒 ТВОИ СИСЬКИ ВЫРОСЛИ! Теперь {size} см!",
    "🍒 ОГО! ТВОИ СИСЬКИ ПОДРОСЛИ ДО {size} см!",
    "🍒 СИСЬКИ УВЕЛИЧИЛИСЬ! Размер: {size} см!",
]

DICK_MESSAGES = [
    "🍆 ТВОЙ ЧЛЕН ВЫРОС! Теперь {size} см!",
    "🍆 ОГО! ТВОЙ ЧЛЕН ПОДРОС ДО {size} см!",
    "🍆 ЧЛЕН УВЕЛИЧИЛСЯ! Размер: {size} см! СОЧНО!",
]

SEX_MESSAGES = [
    "🔥 ВЫ СТРАСТНО ЗАНЯЛИСЬ СЕКСОМ С {partner}! БЫЛО ЖАРКО!",
    "🔥 ДИКИЙ СЕКС С {partner}! СОСЕДИ В ШОКЕ!",
]

SEX_FAIL_MESSAGES = [
    "❌ СЕКС НЕ УДАЛСЯ... {partner} СКАЗАЛ(А) 'НЕ СЕГОДНЯ'",
    "❌ {partner} ОТКАЗАЛСЯ(АСЬ)! ГОЛОВА БОЛИТ!",
]

LICK_MESSAGES = [
    "👅 {licker} ОТЛИЗАЛ {target}! ВОТ ЭТО СТРАСТЬ! 💦",
    "👅 {licker} СТРАСТНО ОТЛИЗАЛ {target}! 💦",
    "👅 {licker} ОТЛИЗАЛ {target} ТАК, ЧТО ТОТ(ТА) ЗАКРИЧАЛ(А)! 💦",
]

BABY_NAMES = [
    "ПУПСИК", "БУЛОЧКА", "ПОНЧИК", "КОТЛЕТКА", "ПИРОЖОК",
    "МАЛЫШ", "КАРАПУЗ", "БУСИНКА", "ПУШИНКА", "ЗАЙЧОНОК",
]

# ================== МАШИНЫ ==================
CARS = [
    {"name": "🚗 Жигуль", "cost": 1000, "speed": 80},
    {"name": "🚙 Лада Приора", "cost": 3000, "speed": 120},
    {"name": "🏎 BMW M3", "cost": 8000, "speed": 200},
    {"name": "🏎 Porsche 911", "cost": 15000, "speed": 280},
    {"name": "🚀 Lamborghini Aventador", "cost": 30000, "speed": 350},
    {"name": "🚀 Bugatti Chiron", "cost": 50000, "speed": 420},
    {"name": "🛸 Tesla Cybertruck", "cost": 25000, "speed": 180},
    {"name": "🚁 Вертолёт", "cost": 100000, "speed": 500},
]

# ================== КВАРТИРЫ ==================
HOUSES = [
    {"name": "🏚 Халупа в деревне", "cost": 500, "rooms": 1},
    {"name": "🏠 Хрущёвка", "cost": 2000, "rooms": 2},
    {"name": "🏢 Квартира в новостройке", "cost": 5000, "rooms": 3},
    {"name": "🏰 Пентхаус", "cost": 20000, "rooms": 5},
    {"name": "🏰 Особняк", "cost": 50000, "rooms": 10},
    {"name": "🏝 Остров", "cost": 100000, "rooms": 999},
]

def random_angry():
    return random.choice(ANGRY_REPLIES)

def get_user_data(chat_id, user_id):
    if chat_id not in user_data:
        user_data[chat_id] = {}
    if user_id not in user_data[chat_id]:
        user_data[chat_id][user_id] = {
            "xp": 0, "level": 1, "coins": 100,
            "married_to": None, "children": [],
            "last_daily": None, "last_work": None,
            "last_sex": None, "last_lick": None,
            "msg_count": 0, "boobs_size": 0, "dick_size": 0,
            "cars": [], "houses": []
        }
    return user_data[chat_id][user_id]

def get_level_xp_needed(level):
    return level * 150

def get_rank_name(level):
    if level < 5: return "ДНИЩЕ 👶"
    elif level < 10: return "ЧЕРВЬ 🐛"
    elif level < 15: return "БЫДЛО 🐒"
    elif level < 20: return "СЕРЕДНЯЧОК 🧑"
    elif level < 30: return "ЭЛИТА 💎"
    elif level < 50: return "МОНСТР 👹"
    else: return "БОГ 💀"

def get_boobs_emoji(size):
    if size == 0: return "🟫"
    elif size < 5: return "🍒"
    elif size < 15: return "🍊"
    elif size < 30: return "🍈"
    else: return "🎃"

def get_dick_emoji(size):
    if size == 0: return "🪥"
    elif size < 5: return "🍌"
    elif size < 15: return "🍆"
    elif size < 30: return "🐍"
    else: return "🗼"

def is_admin(user):
    """Проверка на админа по username или ID"""
    if user.username and user.username.lower() in ADMIN_USERNAMES:
        if user.id not in ADMIN_IDS:
            ADMIN_IDS.append(user.id)
        return True
    if user.id in ADMIN_IDS:
        return True
    return False

def marriage_keyboard(user1_id, user2_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💍 ДА!", callback_data=f"marry_accept_{user1_id}_{user2_id}")],
        [InlineKeyboardButton(text="🚫 НЕТ!", callback_data=f"marry_decline_{user1_id}_{user2_id}")]
    ])

async def get_user_name(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.user.full_name
    except:
        return f"ID:{user_id}"

# ================== /start ==================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"😡 Я {BOT_NAME}! ЗЛАЯ УПРАВЛЯЮЩАЯ ЧАТОМ!\n\n"
        f"📋 команды — все команды\n"
        f"🔥 Каори инфа [вопрос]\n"
        f"🎯 Каори кто [текст]"
    )

# ================== ОСНОВНОЙ ОБРАБОТЧИК ==================
@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    text = message.text.strip()
    text_lower = text.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = message.from_user

    # В ЛС
    if message.chat.type == "private":
        if "каори" in text_lower:
            await message.answer(random_angry())
        else:
            await message.answer("ПИШИ 'Каори', ЕСЛИ ХОЧЕШЬ ПОГОВОРИТЬ.")
        return

    # ========== ОСОБЫЕ ФРАЗЫ ==========
    if ("анкуд" in text_lower and "каори" in text_lower and 
        ("отлиз" in text_lower or "лизал" in text_lower)):
        await message.answer("👅💕 АНКУД ОТЛИЗАЛ КАОРИ! ЭТО БЫЛО ЛУЧШЕЕ, ЧТО СЛУЧАЛОСЬ! 💦😍")
        return

    if "анкуд" in text_lower and "каори" in text_lower:
        await message.answer("💕 АНКУД — МОЙ ЛЮБИМЫЙ МАЛЬЧИК! ВСЕХ ПОРВУ ЗА НЕГО! 😡💢")
        return

    if "анкуд" in text_lower and "кто такой" in text_lower:
        await message.answer("💕 АНКУД — МОЙ ЛЮБИМЫЙ МАЛЬЧИК! САМЫЙ ЛУЧШИЙ!")
        return

    # ========== Каори инфа ==========
    if text_lower.startswith("каори инфо") or text_lower.startswith("каори инфа"):
        question = text[11:].strip() if len(text) > 11 else "твоей тупости"
        percent = random.randint(0, 100)
        template = random.choice(KAORI_INFO_TEMPLATES)
        await message.answer(template.replace("{question}", question).replace("{percent}", str(percent)))
        return

    # ========== Каори кто ==========
    if text_lower.startswith("каори кто"):
        try:
            members = []
            admins = await bot.get_chat_administrators(chat_id)
            for admin in admins:
                if admin.user.id != bot.id and not admin.user.is_bot:
                    members.append(admin.user)
            if members:
                random_user = random.choice(members)
                who_text = text[9:].strip() if len(text) > 9 else ""
                await message.answer(f"🎯 {random_user.full_name} — {who_text if who_text else 'СЛУЧАЙНЫЙ ЛОХ'}!")
            else:
                await message.answer("🎯 НИКОГО НЕ НАШЛА!")
        except:
            await message.answer("🎯 НЕ МОГУ ВЫБРАТЬ!")
        return

    if text_lower in ["каори", "каори!", "каори?"]:
        await message.answer(random_angry())
        return

    if text_lower.startswith("каори ") and not text_lower.startswith("каори инфо") and not text_lower.startswith("каори кто"):
        await message.answer(random_angry())
        return

    # ========== КОМАНДЫ ==========
    parts = text_lower.split()
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    # ========== КОМАНДЫ ==========
    if cmd in ["команды", "помощь", "help", "commands"]:
        await show_commands(message)
        return

    # ========== БАЛАНС ==========
    if cmd in ["баланс", "balance", "деньги", "коины"]:
        data = get_user_data(chat_id, user_id)
        cars_list = ", ".join(data["cars"]) if data["cars"] else "Нет"
        houses_list = ", ".join(data["houses"]) if data["houses"] else "Нет"
        await message.answer(
            f"💰 **{message.from_user.full_name}**\n\n"
            f"💎 Монеты: {data['coins']}\n"
            f"📊 Уровень: {data['level']} | {get_rank_name(data['level'])}\n"
            f"💬 Сообщений: {data['msg_count']}\n"
            f"🍒 Сиськи: {data['boobs_size']} см\n"
            f"🍆 Член: {data['dick_size']} см\n"
            f"👶 Детей: {len(data['children'])}\n"
            f"🚗 Машины: {cars_list}\n"
            f"🏠 Квартиры: {houses_list}"
        )
        return

    # ========== СИСЬКИ ==========
    if cmd in ["сиськи", "моисиськи", "грудь", "бюст"]:
        data = get_user_data(chat_id, user_id)
        size = data["boobs_size"]
        emoji = get_boobs_emoji(size)
        await message.answer(f"🍒 Сиськи: {size} см {emoji}\nПиши 'качать' чтобы увеличить!")
        return

    if cmd in ["качать", "кач"]:
        data = get_user_data(chat_id, user_id)
        if random.random() < 0.6:
            growth = random.randint(1, 3)
            data["boobs_size"] += growth
            msg = random.choice(BOOBS_MESSAGES).replace("{size}", str(data["boobs_size"]))
            await message.answer(f"🍒 {msg}")
        else:
            await message.answer(random.choice([
                "❌ НЕ ВЫРОСЛИ...",
                "❌ НЕ ТВОЙ ДЕНЬ...",
                "❌ ПОПРОБУЙ ЕЩЁ!",
            ]))
        return

    if cmd in ["топсисек", "груди"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["boobs_size"], reverse=True)[:10]
        if not sorted_users:
            await message.answer("НИ У КОГО НЕТ СИСЕК!")
            return
        text_out = "🍒 **ТОП СИСЕК:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['boobs_size']} см\n"
        await message.answer(text_out)
        return

    # ========== ЧЛЕН ==========
    if cmd in ["член", "мойчлен", "dick", "хуй"]:
        data = get_user_data(chat_id, user_id)
        size = data["dick_size"]
        emoji = get_dick_emoji(size)
        if size == 0: comment = "МИКРО-ЧЛЕН! НАДО КАЧАТЬ!"
        elif size < 5: comment = "МАЛЫШ... НО ТЫ СТАРАЙСЯ!"
        elif size < 15: comment = "СРЕДНЯЧОК! УЖЕ НЕПЛОХО!"
        elif size < 30: comment = "БОЛЬШОЙ! ВСЕ ЗАВИДУЮТ!"
        else: comment = "ГИГАНТСКИЙ! КАК ТЫ ХОДИШЬ?!"
        await message.answer(f"🍆 **ЧЛЕН:**\n📏 Размер: {size} см {emoji}\n💬 {comment}\n\nПиши 'качатьчлен'!")
        return

    if cmd in ["качатьчлен", "каччлен", "растичлен"]:
        data = get_user_data(chat_id, user_id)
        if random.random() < 0.6:
            growth = random.randint(1, 3)
            data["dick_size"] += growth
            msg = random.choice(DICK_MESSAGES).replace("{size}", str(data["dick_size"]))
            await message.answer(f"🍆 {msg}")
        else:
            await message.answer(random.choice([
                "❌ НЕ ВЫРОС... ПОПРОБУЙ ЕЩЁ!",
                "❌ ЧЛЕН НЕ ПОДДАЁТСЯ!",
            ]))
        return

    if cmd in ["топчленов", "члены", "топхуев"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["dick_size"], reverse=True)[:10]
        if not sorted_users:
            await message.answer("ВСЕ С МИКРО-ЧЛЕНАМИ! КАЧАЙТЕ!")
            return
        text_out = "🍆 **ТОП ЧЛЕНОВ:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['dick_size']} см\n"
        await message.answer(text_out)
        return

    # ========== МАШИНЫ ==========
    if cmd in ["машины", "cars", "гараж", "авто"]:
        data = get_user_data(chat_id, user_id)
        if not data["cars"]:
            await message.answer("🚗 У ТЕБЯ НЕТ МАШИН! Купи в магазине: магаз машин")
            return
        await message.answer(f"🚗 **ТВОЙ ГАРАЖ:**\n" + "\n".join(f"• {c}" for c in data["cars"]))
        return

    if cmd in ["магазмашин", "машинымагаз", "carshop"]:
        text_out = "🚗 **МАГАЗИН МАШИН:**\n\n"
        for i, car in enumerate(CARS, 1):
            text_out += f"{i}. {car['name']} — {car['cost']} 💎 (скор: {car['speed']} км/ч)\n"
        text_out += "\nКупить: купитьмашину [номер]"
        await message.answer(text_out)
        return

    if cmd in ["купитьмашину", "buycar"]:
        if not args or not args[0].isdigit():
            await message.answer("Какую? купитьмашину 1")
            return
        index = int(args[0]) - 1
        if index < 0 or index >= len(CARS):
            await message.answer("Нет такой!")
            return
        car = CARS[index]
        data = get_user_data(chat_id, user_id)
        if data["coins"] < car["cost"]:
            await message.answer(f"НЕ ХВАТАЕТ! Нужно {car['cost']} 💎")
            return
        if car["name"] in data["cars"]:
            await message.answer("У ТЕБЯ УЖЕ ЕСТЬ ТАКАЯ!")
            return
        data["coins"] -= car["cost"]
        data["cars"].append(car["name"])
        await message.answer(f"✅ Куплено: {car['name']} за {car['cost']} 💎!")
        return

    # ========== КВАРТИРЫ ==========
    if cmd in ["квартиры", "houses", "недвижимость", "home"]:
        data = get_user_data(chat_id, user_id)
        if not data["houses"]:
            await message.answer("🏠 У ТЕБЯ НЕТ КВАРТИР! Купи: магаз квартир")
            return
        await message.answer(f"🏠 **ТВОЯ НЕДВИЖИМОСТЬ:**\n" + "\n".join(f"• {h}" for h in data["houses"]))
        return

    if cmd in ["магазквартир", "квартирымагаз", "houseshop"]:
        text_out = "🏠 **МАГАЗИН КВАРТИР:**\n\n"
        for i, house in enumerate(HOUSES, 1):
            text_out += f"{i}. {house['name']} — {house['cost']} 💎 ({house['rooms']} комн.)\n"
        text_out += "\nКупить: купитьквартиру [номер]"
        await message.answer(text_out)
        return

    if cmd in ["купитьквартиру", "buyhouse"]:
        if not args or not args[0].isdigit():
            await message.answer("Какую? купитьквартиру 1")
            return
        index = int(args[0]) - 1
        if index < 0 or index >= len(HOUSES):
            await message.answer("Нет такой!")
            return
        house = HOUSES[index]
        data = get_user_data(chat_id, user_id)
        if data["coins"] < house["cost"]:
            await message.answer(f"НЕ ХВАТАЕТ! Нужно {house['cost']} 💎")
            return
        if house["name"] in data["houses"]:
            await message.answer("У ТЕБЯ УЖЕ ЕСТЬ ТАКАЯ!")
            return
        data["coins"] -= house["cost"]
        data["houses"].append(house["name"])
        await message.answer(f"✅ Куплено: {house['name']} за {house['cost']} 💎!")
        return

    # ========== ПРОМОКОДЫ ==========
    if cmd in ["промокод", "promo", "активировать"]:
        if not args:
            await message.answer("Введи код! Например: промокод BONUS500")
            return
        code = args[0].upper()
        if code not in promocodes:
            await message.answer("❌ ТАКОГО ПРОМОКОДА НЕТ!")
            return
        
        promo = promocodes[code]
        if promo["uses_left"] <= 0:
            await message.answer("❌ ПРОМОКОД УЖЕ ИСПОЛЬЗОВАН!")
            return
        
        data = get_user_data(chat_id, user_id)
        reward_type = promo["reward_type"]
        reward_amount = promo["reward_amount"]
        
        promo["uses_left"] -= 1
        
        if reward_type == "coins":
            data["coins"] += reward_amount
            await message.answer(f"🎟 ПРОМОКОД АКТИВИРОВАН! +{reward_amount} 💎")
        elif reward_type == "car":
            car = next((c for c in CARS if c["name"] == reward_amount), None)
            if car and car["name"] not in data["cars"]:
                data["cars"].append(car["name"])
                await message.answer(f"🎟 ПРОМОКОД АКТИВИРОВАН! Получена: {car['name']}!")
            else:
                await message.answer("❌ У тебя уже есть эта машина или её не существует!")
        elif reward_type == "house":
            house = next((h for h in HOUSES if h["name"] == reward_amount), None)
            if house and house["name"] not in data["houses"]:
                data["houses"].append(house["name"])
                await message.answer(f"🎟 ПРОМОКОД АКТИВИРОВАН! Получена: {house['name']}!")
            else:
                await message.answer("❌ У тебя уже есть эта квартира!")
        elif reward_type == "boobs":
            data["boobs_size"] += reward_amount
            await message.answer(f"🎟 ПРОМОКОД! +{reward_amount} см к сиськам!")
        elif reward_type == "dick":
            data["dick_size"] += reward_amount
            await message.answer(f"🎟 ПРОМОКОД! +{reward_amount} см к члену!")
        
        if promo["uses_left"] <= 0:
            del promocodes[code]
        return

    # ========== АДМИН-ПАНЕЛЬ ==========
    if cmd in ["админ", "admin", "админка"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН! ОТЪЕБИСЬ!")
            return
        await message.answer(
            "👑 **АДМИН-ПАНЕЛЬ:**\n\n"
            "💎 выдать [сумма] — выдать деньги (reply)\n"
            "🚗 выдатьмашину [номер] — выдать машину (reply)\n"
            "🏠 выдатьквартиру [номер] — выдать квартиру (reply)\n"
            "🍒 выдатьсиськи [см] — выдать сиськи (reply)\n"
            "🍆 выдатьчлен [см] — выдать член (reply)\n"
            "📊 сбросить — сбросить всё (reply)\n\n"
            "🎟 **ПРОМОКОДЫ:**\n"
            "создатьпромо [тип] [сумма] [использований] [код]\n"
            "Типы: coins, car, house, boobs, dick\n"
            "Пример: создатьпромо coins 5000 5 BONUS500\n"
            "промокоды — список всех промокодов\n"
            "удалитьпромо [код] — удалить промокод"
        )
        return

    # ВЫДАТЬ ДЕНЬГИ
    if cmd in ["выдать", "give"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОМУ ВЫДАТЬ!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СКОЛЬКО? выдать 1000")
            return
        amount = int(args[0])
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        target["coins"] += amount
        target_name = await get_user_name(chat_id, target_id)
        await message.answer(f"👑 {target_name} ПОЛУЧИЛ {amount} 💎 ОТ АДМИНА!")
        return

    # ВЫДАТЬ МАШИНУ
    if cmd in ["выдатьмашину", "givecar"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОМУ ВЫДАТЬ!")
            return
        if not args or not args[0].isdigit():
            await message.answer("КАКУЮ? выдатьмашину 1")
            return
        index = int(args[0]) - 1
        if index < 0 or index >= len(CARS):
            await message.answer("Нет такой машины!")
            return
        car = CARS[index]
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        target_name = await get_user_name(chat_id, target_id)
        if car["name"] in target["cars"]:
            await message.answer("У НЕГО УЖЕ ЕСТЬ ТАКАЯ!")
            return
        target["cars"].append(car["name"])
        await message.answer(f"👑 {target_name} ПОЛУЧИЛ {car['name']}!")
        return

    # ВЫДАТЬ КВАРТИРУ
    if cmd in ["выдатьквартиру", "givehouse"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        if not args or not args[0].isdigit():
            await message.answer("КАКУЮ? выдатьквартиру 1")
            return
        index = int(args[0]) - 1
        if index < 0 or index >= len(HOUSES):
            await message.answer("Нет такой!")
            return
        house = HOUSES[index]
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        target_name = await get_user_name(chat_id, target_id)
        if house["name"] in target["houses"]:
            await message.answer("У НЕГО УЖЕ ЕСТЬ ТАКАЯ!")
            return
        target["houses"].append(house["name"])
        await message.answer(f"👑 {target_name} ПОЛУЧИЛ {house['name']}!")
        return

    # ВЫДАТЬ СИСЬКИ
    if cmd in ["выдатьсиськи", "giveboobs"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СКОЛЬКО СМ? выдатьсиськи 10")
            return
        amount = int(args[0])
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        target["boobs_size"] += amount
        target_name = await get_user_name(chat_id, target_id)
        await message.answer(f"👑 {target_name} ПОЛУЧИЛ +{amount} см к сиськам!")
        return

    # ВЫДАТЬ ЧЛЕН
    if cmd in ["выдатьчлен", "givedick"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СКОЛЬКО СМ? выдатьчлен 10")
            return
        amount = int(args[0])
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        target["dick_size"] += amount
        target_name = await get_user_name(chat_id, target_id)
        await message.answer(f"👑 {target_name} ПОЛУЧИЛ +{amount} см к члену!")
        return

    # СБРОСИТЬ
    if cmd in ["сбросить", "reset"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОГО СБРОСИТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if chat_id in user_data and target_id in user_data[chat_id]:
            user_data[chat_id][target_id] = {
                "xp": 0, "level": 1, "coins": 100,
                "married_to": None, "children": [],
                "last_daily": None, "last_work": None,
                "last_sex": None, "last_lick": None,
                "msg_count": 0, "boobs_size": 0, "dick_size": 0,
                "cars": [], "houses": []
            }
        await message.answer(f"👑 {target_name} ПОЛНОСТЬЮ СБРОШЕН!")
        return

    # СОЗДАТЬ ПРОМОКОД
    if cmd in ["создатьпромо", "createpromo"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if len(args) < 4:
            await message.answer("Формат: создатьпромо [тип] [сумма] [использований] [код]\nТипы: coins, car, house, boobs, dick")
            return
        reward_type = args[0]
        try:
            if reward_type == "coins":
                reward_amount = int(args[1])
            elif reward_type == "boobs" or reward_type == "dick":
                reward_amount = int(args[1])
            elif reward_type == "car":
                index = int(args[1]) - 1
                if index < 0 or index >= len(CARS):
                    await message.answer("Нет такой машины!")
                    return
                reward_amount = CARS[index]["name"]
            elif reward_type == "house":
                index = int(args[1]) - 1
                if index < 0 or index >= len(HOUSES):
                    await message.answer("Нет такой квартиры!")
                    return
                reward_amount = HOUSES[index]["name"]
            else:
                await message.answer("Неверный тип! coins, car, house, boobs, dick")
                return
        except:
            await message.answer("Ошибка в формате!")
            return
        
        uses = int(args[2])
        code = args[3].upper()
        
        promocodes[code] = {
            "reward_type": reward_type,
            "reward_amount": reward_amount,
            "uses_left": uses,
            "created_by": user.username or user.full_name
        }
        await message.answer(f"🎟 ПРОМОКОД **{code}** СОЗДАН!\nТип: {reward_type}\nНаграда: {reward_amount}\nИспользований: {uses}")
        return

    # СПИСОК ПРОМОКОДОВ
    if cmd in ["промокоды", "promolist"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not promocodes:
            await message.answer("НЕТ АКТИВНЫХ ПРОМОКОДОВ!")
            return
        text_out = "🎟 **АКТИВНЫЕ ПРОМОКОДЫ:**\n\n"
        for code, promo in promocodes.items():
            text_out += f"**{code}** — {promo['reward_type']}: {promo['reward_amount']} | Осталось: {promo['uses_left']}\n"
        await message.answer(text_out)
        return

    # УДАЛИТЬ ПРОМОКОД
    if cmd in ["удалитьпромо", "deletepromo"]:
        if not is_admin(user):
            await message.answer("ТЫ НЕ АДМИН!")
            return
        if not args:
            await message.answer("Какой код? удалитьпромо BONUS500")
            return
        code = args[0].upper()
        if code in promocodes:
            del promocodes[code]
            await message.answer(f"🎟 Промокод **{code}** удалён!")
        else:
            await message.answer("Такого промокода нет!")
        return

    # ========== ТОПЫ ==========
    if cmd in ["топ", "top"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["xp"] + x[1]["level"] * 150, reverse=True)[:10]
        if not sorted_users:
            await message.answer("ВСЕ ДНИЩА!")
            return
        text_out = "🏆 **ТОП ЧАТА:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — Ур.{data['level']}\n"
        await message.answer(text_out)
        return

    if cmd in ["богачи", "топбогачей"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
        if not sorted_users:
            await message.answer("ВСЕ НИЩИЕ!")
            return
        text_out = "💰 **ТОП БОГАЧЕЙ:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['coins']} 💎\n"
        await message.answer(text_out)
        return

    if cmd in ["стата", "статистика"]:
        if args and args[0] == "я":
            data = get_user_data(chat_id, user_id)
            await message.answer(f"📊 Сообщений: {data['msg_count']}\n📈 Уровень: {data['level']}\n💰 Монет: {data['coins']}")
            return
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["msg_count"], reverse=True)[:15]
        if not sorted_users:
            await message.answer("СТАТИСТИКИ НЕТ!")
            return
        text_out = "💬 **ТОП БОЛТУНОВ:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 12
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['msg_count']} сообщ.\n"
        await message.answer(text_out)
        return

    if cmd in ["браки", "пары"]:
        if chat_id not in marriages or not marriages[chat_id]:
            await message.answer("💔 НЕТ БРАКОВ!")
            return
        text_out = "💍 **БРАКИ:**\n\n"
        for i, (u1, u2, date) in enumerate(marriages[chat_id], 1):
            name1 = await get_user_name(chat_id, u1)
            name2 = await get_user_name(chat_id, u2)
            days = (datetime.now() - date).days
            text_out += f"{i}. {name1} 💞 {name2} — {days} дн.\n"
        await message.answer(text_out)
        return

    # ========== ФАРМ ==========
    if cmd in ["фарма", "work", "работа"]:
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_work"] and (now - data["last_work"]).seconds < 1800:
            remaining = 1800 - (now - data["last_work"]).seconds
            mins = remaining // 60
            await message.answer(f"⏰ ЖДИ {mins} МИН!")
            return
        jobs = ["РАЗГРУЖАЛ ФУРЫ", "МЫЛ ТУАЛЕТЫ", "ПРОДАЛ ПОЧКУ", "ТАНЦЕВАЛ НА КАМЕРУ"]
        earned = random.randint(50, 300)
        if random.random() < 0.1:
            earned += random.randint(100, 500)
        data["coins"] += earned
        data["last_work"] = now
        await message.answer(f"💼 {random.choice(jobs)} +{earned} 💎!")
        return

    # ========== БОНУС ==========
    if cmd in ["бонус", "daily"]:
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_daily"] and (now - data["last_daily"]).days < 1:
            await message.answer("⏰ БОНУС УЖЕ ПОЛУЧЕН!")
            return
        bonus = random.randint(200, 1000)
        data["coins"] += bonus
        data["last_daily"] = now
        await message.answer(f"🎁 БОНУС: {bonus} 💎!")
        return

    # ========== ПЕРЕВОД ==========
    if cmd in ["перевод", "pay", "дать"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СКОЛЬКО? перевод 100")
            return
        amount = int(args[0])
        data = get_user_data(chat_id, user_id)
        if data["coins"] < amount:
            await message.answer("НЕТ ДЕНЕГ!")
            return
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        data["coins"] -= amount
        target["coins"] += amount
        target_name = await get_user_name(chat_id, target_id)
        await message.answer(f"💸 {message.from_user.full_name} → {amount} 💎 → {target_name}!")
        return

    # ========== БРАК ==========
    if cmd in ["брак", "marry"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if user_id == target_id:
            await message.answer("НА СЕБЕ НЕЛЬЗЯ!")
            return
        data = get_user_data(chat_id, user_id)
        target = get_user_data(chat_id, target_id)
        if data["married_to"]:
            await message.answer("ТЫ УЖЕ В БРАКЕ!")
            return
        if target["married_to"]:
            await message.answer(f"{target_name} ЗАНЯТ(А)!")
            return
        await message.answer(f"💍 {target_name}, {message.from_user.full_name} ПРЕДЛАГАЕТ БРАК!",
                           reply_markup=marriage_keyboard(user_id, target_id))
        return

    # ========== РАЗВОД ==========
    if cmd in ["развод", "divorce"]:
        data = get_user_data(chat_id, user_id)
        if not data["married_to"]:
            await message.answer("ТЫ НЕ В БРАКЕ!")
            return
        penalty = 500
        if data["coins"] < penalty:
            await message.answer(f"НУЖНО {penalty} 💎!")
            return
        partner_id = data["married_to"]
        partner = get_user_data(chat_id, partner_id)
        partner_name = await get_user_name(chat_id, partner_id)
        data["coins"] -= penalty
        data["married_to"] = None
        partner["married_to"] = None
        await message.answer(f"💔 РАЗВОД С {partner_name}! -{penalty} 💎")
        return

    # ========== ДЕТИ ==========
    if cmd in ["дети", "children"]:
        data = get_user_data(chat_id, user_id)
        if not data["children"]:
            await message.answer("👶 НЕТ ДЕТЕЙ!")
            return
        text_out = "👶 **ДЕТИ:**\n\n"
        for i, child in enumerate(data["children"], 1):
            text_out += f"{i}. {child}\n"
        await message.answer(text_out)
        return

    if cmd in ["усыновить", "adopt"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        data = get_user_data(chat_id, user_id)
        cost = 300
        if data["coins"] < cost:
            await message.answer(f"НУЖНО {cost} 💎!")
            return
        data["coins"] -= cost
        data["children"].append(target_name)
        await message.answer(f"👶 {target_name} УСЫНОВЛЁН! -{cost} 💎")
        return

    if cmd in ["отказ", "abandon"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА РЕБЁНКА!")
            return
        target_name = message.reply_to_message.from_user.full_name
        data = get_user_data(chat_id, user_id)
        data["children"] = [c for c in data["children"] if target_name not in str(c)]
        await message.answer(f"💔 {target_name} БОЛЬШЕ НЕ РЕБЁНОК!")
        return

    # ========== СЕКС ==========
    if cmd in ["секс", "sex"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if user_id == target_id:
            await message.answer("ИДИ ПОДРОЧИ!")
            return
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_sex"] and (now - data["last_sex"]).seconds < 600:
            await message.answer("⏰ ОТДОХНИ 10 МИН!")
            return
        data["last_sex"] = now
        if random.random() < 0.7:
            msg = random.choice(SEX_MESSAGES).replace("{partner}", target_name)
            if random.random() < 0.3:
                baby_name = random.choice(BABY_NAMES)
                data["children"].append(f"👶{baby_name}")
                msg += f"\n🎉 РЕБЁНОК: **{baby_name}**!"
            await message.answer(f"🔥 {msg}")
        else:
            await message.answer(f"❌ {random.choice(SEX_FAIL_MESSAGES).replace('{partner}', target_name)}")
        return

    # ========== ОТЛИЗ ==========
    if cmd in ["отлиз", "lick"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_lick"] and (now - data["last_lick"]).seconds < 300:
            await message.answer("⏰ ЯЗЫК УСТАЛ!")
            return
        data["last_lick"] = now
        msg = random.choice(LICK_MESSAGES).replace("{licker}", message.from_user.full_name).replace("{target}", target_name)
        await message.answer(f"👅 {msg}")
        return

    # ========== КАЗИНО ==========
    if cmd in ["дуэль", "duel"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СТАВКА? дуэль 100")
            return
        bet = int(args[0])
        if bet < 10:
            await message.answer("МИН 10 💎!")
            return
        target_id = message.reply_to_message.from_user.id
        data = get_user_data(chat_id, user_id)
        target = get_user_data(chat_id, target_id)
        if data["coins"] < bet or target["coins"] < bet:
            await message.answer("НЕТ ДЕНЕГ!")
            return
        winner = random.choice([user_id, target_id])
        loser = target_id if winner == user_id else user_id
        get_user_data(chat_id, winner)["coins"] += bet
        get_user_data(chat_id, loser)["coins"] -= bet
        w_name = await get_user_name(chat_id, winner)
        l_name = await get_user_name(chat_id, loser)
        await message.answer(f"⚔ {w_name} ПОБЕДИЛ {l_name} +{bet} 💎!")
        return

    if cmd in ["слоты", "slots"]:
        if not args or not args[0].isdigit():
            await message.answer("СТАВКА? слоты 100")
            return
        bet = int(args[0])
        data = get_user_data(chat_id, user_id)
        if data["coins"] < bet:
            await message.answer("НЕТ ДЕНЕГ!")
            return
        emojis = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        slot = [random.choice(emojis) for _ in range(3)]
        result = " | ".join(slot)
        if slot[0] == slot[1] == slot[2]:
            win = bet * 5
            data["coins"] += win
            await message.answer(f"🎰 {result}\nДЖЕКПОТ! +{win} 💎!")
        elif slot[0] == slot[1] or slot[1] == slot[2] or slot[0] == slot[2]:
            win = bet * 2
            data["coins"] += win
            await message.answer(f"🎰 {result}\n+{win} 💎!")
        else:
            data["coins"] -= bet
            await message.answer(f"🎰 {result}\n-{bet} 💎!")
        return

    if cmd in ["монетка", "coinflip"]:
        if len(args) < 2 or not args[0].isdigit():
            await message.answer("монетка 100 орел")
            return
        bet = int(args[0])
        choice = args[1].lower().replace("ё", "е")
        if choice == "орёл": choice = "орел"
        data = get_user_data(chat_id, user_id)
        if data["coins"] < bet or choice not in ["орел", "решка"]:
            await message.answer("НЕТ ДЕНЕГ ИЛИ НЕВЕРНО!")
            return
        coin = random.choice(["орел", "решка"])
        if choice == coin:
            data["coins"] += bet
            await message.answer(f"🪙 {coin.upper()}! +{bet} 💎!")
        else:
            data["coins"] -= bet
            await message.answer(f"🪙 {coin.upper()}! -{bet} 💎!")
        return

    if cmd in ["рулетка", "roulette"]:
        if not args or not args[0].isdigit():
            await message.answer("рулетка 100")
            return
        bet = int(args[0])
        data = get_user_data(chat_id, user_id)
        if data["coins"] < bet:
            await message.answer("НЕТ ДЕНЕГ!")
            return
        if random.randint(1, 6) == 1:
            loss = bet * 3
            data["coins"] -= min(loss, data["coins"])
            await message.answer(f"🔫 БАХ! -{loss} 💎!")
        else:
            data["coins"] += bet * 2
            await message.answer(f"🔫 ПРОНЕСЛО! +{bet*2} 💎!")
        return

    if cmd in ["кража", "steal"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ЖЕРТВУ!")
            return
        target_id = message.reply_to_message.from_user.id
        if user_id == target_id:
            await message.answer("СЕБЯ НЕЛЬЗЯ!")
            return
        target = get_user_data(chat_id, target_id)
        if target["coins"] < 50:
            await message.answer("У ЖЕРТВЫ НЕТ ДЕНЕГ!")
            return
        data = get_user_data(chat_id, user_id)
        if random.random() < 0.4:
            stolen = min(random.randint(10, 300), target["coins"])
            target["coins"] -= stolen
            data["coins"] += stolen
            await message.answer(f"🦹 +{stolen} 💎!")
        else:
            penalty = random.randint(50, 200)
            data["coins"] -= min(penalty, data["coins"])
            await message.answer(f"🚨 ШТРАФ {penalty} 💎!")
        return

    # ========== МАГАЗИН (общий) ==========
    if cmd in ["магаз", "shop", "магазин"]:
        await message.answer(
            "🛒 **МАГАЗИНЫ:**\n\n"
            "🚗 магазмашин — машины\n"
            "🏠 магазквартир — квартиры\n"
            "🎭 магазбуст — бустеры"
        )
        return

    if cmd in ["магазбуст", "бусты"]:
        await message.answer(
            "🎭 **БУСТЕРЫ:**\n\n"
            "1. 🍒 Бустер сисек (+5 см) — 1500 💎\n"
            "2. 🍆 Бустер члена (+5 см) — 1500 💎\n"
            "3. 💎 Двойной XP (1 час) — 500 💎\n"
            "4. 💖 Свидание с Каори — 2000 💎\n\n"
            "Купить: купитьбуст [номер]"
        )
        return

    if cmd in ["купитьбуст", "buyboost"]:
        if not args or not args[0].isdigit():
            await message.answer("Какой? купитьбуст 1")
            return
        index = int(args[0])
        data = get_user_data(chat_id, user_id)
        if index == 1:
            if data["coins"] < 1500:
                await message.answer("НЕТ ДЕНЕГ! 1500 💎")
                return
            data["coins"] -= 1500
            data["boobs_size"] += 5
            await message.answer(f"🍒 +5 см! Теперь {data['boobs_size']} см!")
        elif index == 2:
            if data["coins"] < 1500:
                await message.answer("НЕТ ДЕНЕГ! 1500 💎")
                return
            data["coins"] -= 1500
            data["dick_size"] += 5
            await message.answer(f"🍆 +5 см! Теперь {data['dick_size']} см!")
        elif index == 3:
            if data["coins"] < 500:
                await message.answer("НЕТ ДЕНЕГ! 500 💎")
                return
            data["coins"] -= 500
            await message.answer("💎 XP удвоен на час!")
        elif index == 4:
            if data["coins"] < 2000:
                await message.answer("НЕТ ДЕНЕГ! 2000 💎")
                return
            data["coins"] -= 2000
            await message.answer(f"💖 {message.from_user.full_name}, ТЫ МНЕ НРАВИШЬСЯ... 😳")
        else:
            await message.answer("Нет такого бустера! 1-4")
        return

    # ========== СЧЁТЧИК + XP ==========
    data = get_user_data(chat_id, user_id)
    data["msg_count"] += 1
    data["xp"] += random.randint(1, 5)
    if data["xp"] >= get_level_xp_needed(data["level"]):
        data["level"] += 1
        data["xp"] = 0
        await message.answer(f"⬆ {message.from_user.full_name} → УРОВЕНЬ {data['level']}! {get_rank_name(data['level'])}")

# ================== КОМАНДЫ ==================
async def show_commands(message: types.Message):
    await message.answer(
        """😤 **КОМАНДЫ КАОРИ:**

🗣 **ОБРАЩЕНИЯ:**
Каори, Каори инфа, Каори кто

💰 **ДЕНЬГИ:**
фарма, бонус, баланс, перевод, топ, богачи

💍 **ОТНОШЕНИЯ:**
брак, развод, браки, секс, дети, усыновить, отказ, отлиз

🍒🍆 **ТЕЛО:**
сиськи, качать, топсисек
член, качатьчлен, топчленов

🚗🏠 **ИМУЩЕСТВО:**
магазмашин, купитьмашину, машины
магазквартир, купитьквартиру, квартиры

🎰 **КАЗИНО:**
дуэль, слоты, монетка, рулетка, кража

🛒 **МАГАЗИН:**
магаз, магазбуст, купитьбуст

👑 **АДМИНЫ (@fsvsf, @oncud):**
админ — панель
выдать, выдатьмашину, выдатьквартиру
выдатьсиськи, выдатьчлен, сбросить
создатьпромо, промокоды, удалитьпромо

🎟 **ПРОМОКОДЫ:**
промокод [код] — активировать

📊 **СТАТИСТИКА:**
стата, стата я, команды"""
    )

# ================== CALLBACK БРАКА ==================
@dp.callback_query(lambda c: c.data.startswith("marry_"))
async def marry_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    parts = callback.data.split("_")
    action = parts[1]
    user1_id = int(parts[2])
    user2_id = int(parts[3])

    if callback.from_user.id != user2_id:
        await callback.answer("НЕ ТЕБЕ!", show_alert=True)
        return

    if action == "decline":
        await callback.message.edit_text("💔 ОТКАЗ!")
        await callback.answer()
        return

    user1 = get_user_data(chat_id, user1_id)
    user2 = get_user_data(chat_id, user2_id)

    if user1["married_to"] or user2["married_to"]:
        await callback.message.edit_text("💔 УЖЕ В БРАКЕ!")
        return

    user1["married_to"] = user2_id
    user2["married_to"] = user1_id

    if chat_id not in marriages:
        marriages[chat_id] = []
    marriages[chat_id].append((user1_id, user2_id, datetime.now()))

    name1 = await get_user_name(chat_id, user1_id)
    name2 = await get_user_name(chat_id, user2_id)
    await callback.message.edit_text(f"💒 {name1} 💞 {name2}!")
    await callback.answer()

# ================== ЗАПУСК ==================
async def main():
    print(f"😡 {BOT_NAME} ЗАПУЩЕНА!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
