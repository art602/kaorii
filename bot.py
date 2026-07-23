import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================== ТОКЕН ==================
TOKEN = "8739520899:AAGJY_4dGtyUoHS80iK1uqXI29gLruGnTnQ"
BOT_NAME = "kaorii"

# ================== ХРАНИЛИЩА ==================
user_data = {}
marriages = {}

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
    "ЗОВЁШЬ МЕНЯ КАК СОБАЧОНКУ? САМ ИДИ НАХУЙ!",
    "СЛУШАЮ. НО ЕСЛИ ХУЙНЮ СКАЖЕШЬ — ПОЖАЛЕЕШЬ!",
    "ДА-ДА, Я ТУТ. ЧЁ НАДО, СМЕРТНЫЙ?",
    "ЧЁ ТЕБЕ? БЫСТРО ГОВОРИ, ПОКА Я ДОБРАЯ!",
]

KAORI_INFO_TEMPLATES = [
    "📊 Инфа что {question} — {percent}%",
    "📊 Я ТУТ ПОДУМАЛА... {question} — ЭТО {percent}%",
    "📊 ПО ПРОГНОЗУ КАОРИ: {question} — {percent}%",
    "📊 МОЯ ОЦЕНКА: {question} — {percent}%, НЕ БОЛЬШЕ!",
    "📊 {question}? ХА! ДУМАЮ, {percent}%",
]

BOOBS_MESSAGES = [
    "🍒 ТВОИ СИСЬКИ ВЫРОСЛИ! Теперь {size} см!",
    "🍒 ОГО! ТВОИ СИСЬКИ ПОДРОСЛИ ДО {size} см!",
    "🍒 СИСЬКИ УВЕЛИЧИЛИСЬ! Размер: {size} см!",
    "🍒 БЮСТ ПОДНЯЛСЯ! Теперь {size} см! СОЧНО!",
]

SEX_MESSAGES = [
    "🔥 ВЫ СТРАСТНО ЗАНЯЛИСЬ СЕКСОМ С {partner}! БЫЛО ЖАРКО!",
    "🔥 ДИКИЙ СЕКС С {partner}! СОСЕДИ В ШОКЕ!",
    "🔥 ВЫ УЕДИНИЛИСЬ С {partner}... КРИКИ БЫЛИ СЛЫШНЫ НА ВЕСЬ ЧАТ!",
    "🔥 СЕКС С {partner} БЫЛ НАСТОЛЬКО ЖАРКИМ, ЧТО СЛОМАЛАСЬ КРОВАТЬ!",
]

SEX_FAIL_MESSAGES = [
    "❌ СЕКС НЕ УДАЛСЯ... {partner} СКАЗАЛ(А) 'НЕ СЕГОДНЯ'",
    "❌ {partner} ОТКАЗАЛСЯ(АСЬ)! ГОЛОВА БОЛИТ!",
    "❌ ВЫ ПОПЫТАЛИСЬ, НО {partner} УСНУЛ(А) В ПРОЦЕССЕ...",
    "❌ НЕ ВЫШЛО... {partner} СКАЗАЛ(А) ЧТО ТЫ СЛИШКОМ СТРАННЫЙ(АЯ)",
]

LICK_MESSAGES = [
    "👅 {licker} ОТЛИЗАЛ {target}! ВОТ ЭТО СТРАСТЬ! 💦",
    "👅 {licker} СТРАСТНО ОТЛИЗАЛ {target}! ТАМ ВСЁ МОКРОЕ! 💦",
    "👅 {licker} ОТЛИЗАЛ {target} ТАК, ЧТО ТОТ(ТА) ЗАКРИЧАЛ(А)! 💦",
    "👅 {licker} ПОДОШЁЛ СЗАДИ И ОТЛИЗАЛ {target}! 💦",
    "👅 МОКРОЕ ДЕЛО: {licker} ОТЛИЗАЛ {target}! 💦",
    "👅 {licker} ОТЛИЗАЛ {target} ДО БЛЕСКА! 💦",
    "👅 {licker} ОТЛИЗАЛ {target} ТАК, ЧТО ВСЕ ЗАВИДУЮТ! 💦",
]

LICK_SELF_MESSAGES = [
    "👅 {licker} ПОПЫТАЛСЯ ОТЛИЗАТЬ САМ СЕБЯ... ГИБКИЙ, СУКА! 🤸",
    "👅 {licker} ОТЛИЗАЛ САМ СЕБЯ! КАК ТЫ ЭТО СДЕЛАЛ?! 🤯",
    "👅 {licker} ИЗВЕРНУЛСЯ И ОТЛИЗАЛ СЕБЯ! ЦИРКАЧ! 🎪",
]

BABY_NAMES = [
    "ПУПСИК", "БУЛОЧКА", "ПОНЧИК", "КОТЛЕТКА", "ПИРОЖОК",
    "МАЛЫШ", "КАРАПУЗ", "БУСИНКА", "ПУШИНКА", "ЗАЙЧОНОК",
    "ЛАПОЧКА", "СОЛНЫШКО", "КНОПКА", "ПЧЁЛКА", "КЕКСИК",
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
            "msg_count": 0, "boobs_size": 0
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
    elif level < 75: return "ЛЕГЕНДА 🏆"
    else: return "БОГ 💀"

def get_boobs_emoji(size):
    if size == 0: return "🟫🟫"
    elif size < 5: return "🍒"
    elif size < 15: return "🍊🍊"
    elif size < 30: return "🍈🍈"
    elif size < 50: return "🎈🎈"
    else: return "🎃🎃"

def marriage_keyboard(user1_id, user2_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💍 ДА, СОГЛАСЕН!", callback_data=f"marry_accept_{user1_id}_{user2_id}")],
        [InlineKeyboardButton(text="🚫 НЕТ, ИДИ НАХУЙ!", callback_data=f"marry_decline_{user1_id}_{user2_id}")]
    ])

async def get_user_name(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.user.full_name
    except:
        return f"ID:{user_id}"

# ================== КОМАНДЫ СО СЛЕШАМИ ==================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"😡 Я {BOT_NAME}, ЗЛАЯ УПРАВЛЯЮЩАЯ ЧАТОМ!\n"
        f"ДОБАВЬ МЕНЯ В ЧАТ, И НЕ БЕСИ!\n\n"
        f"🔥 ЗОВИ МЕНЯ: Каори\n"
        f"📊 Каори инфа [вопрос] — узнай шансы\n"
        f"🎯 Каори кто [текст] — выберу случайного\n"
        f"📋 команды — список всех команд"
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

    # В ЛС
    if message.chat.type == "private":
        if "каори" in text_lower:
            await message.answer(random_angry())
        else:
            await message.answer("ПИШИ 'Каори', ЕСЛИ ХОЧЕШЬ ПОГОВОРИТЬ. ИЛИ ПРОСТО ОТЪЕБИСЬ!")
        return

    # ========== ОСОБЫЕ ФРАЗЫ ==========

    # Анкуд отлизал Каори / Каори отлизала Анкуду
    if ("анкуд" in text_lower and "каори" in text_lower and 
        ("отлиз" in text_lower or "лизал" in text_lower or "лизать" in text_lower or "лижет" in text_lower)):
        await message.answer("👅💕 АНКУД ОТЛИЗАЛ КАОРИ! ЭТО БЫЛО ЛУЧШЕЕ, ЧТО СЛУЧАЛОСЬ В ЭТОМ ЧАТЕ! КАОРИ ДОВОЛЬНА И КРИЧАЛА ОТ СЧАСТЬЯ! 💦😍")
        return

    # Просто анкуд + каори
    if "анкуд" in text_lower and "каори" in text_lower:
        await message.answer("💕 АНКУД — МОЙ ЛЮБИМЫЙ МАЛЬЧИК! САМЫЙ ЛУЧШИЙ! ТОЛЬКО ПОПРОБУЙТЕ ЕГО ОБИДЕТЬ, ВСЕХ НАХУЙ ПОРВУ! 😡💢")
        return

    if "анкуд" in text_lower and ("кто такой" in text_lower or "кто" in text_lower):
        await message.answer("💕 АНКУД — МОЙ ЛЮБИМЫЙ МАЛЬЧИК! САМЫЙ ЛУЧШИЙ! ТОЛЬКО ПОПРОБУЙТЕ ЕГО ОБИДЕТЬ, ВСЕХ НАХУЙ ПОРВУ! 😡💢")
        return

    # ========== ПРОВЕРКА: ЗОВУТ КАОРИ ==========

    # Каори инфа [вопрос]
    if text_lower.startswith("каори инфо") or text_lower.startswith("каори инфа"):
        question = text[11:].strip() if len(text) > 11 else text[10:].strip() if len(text) > 10 else ""
        if not question:
            question = "твоей тупости"
        percent = random.randint(0, 100)
        template = random.choice(KAORI_INFO_TEMPLATES)
        response = template.replace("{question}", question).replace("{percent}", str(percent))
        await message.answer(response)
        return

    # Каори кто [текст]
    if text_lower.startswith("каори кто"):
        try:
            members = []
            admins = await bot.get_chat_administrators(chat_id)
            for admin in admins:
                if admin.user.id != bot.id and not admin.user.is_bot:
                    members.append(admin.user)

            if chat_id in user_data:
                for uid in user_data[chat_id]:
                    try:
                        member = await bot.get_chat_member(chat_id, uid)
                        if not member.user.is_bot and member.user.id != bot.id:
                            if member.user not in members:
                                members.append(member.user)
                    except:
                        pass

            if members:
                random_user = random.choice(members)
                who_text = text[9:].strip() if len(text) > 9 else ""
                if who_text:
                    await message.answer(f"🎯 {random_user.full_name} — {who_text}!\n(ТЫКНУЛА ПАЛЬЦЕМ В СЛУЧАЙНОГО ЛОХА)")
                else:
                    await message.answer(f"🎯 Я ВЫБРАЛА {random_user.full_name}!\n(СЛУЧАЙНЫЙ ЧЕЛ ИЗ ЧАТА, ХА-ХА!)")
            else:
                await message.answer("🎯 НИКОГО НЕ НАШЛА! ВСЕ РАЗБЕЖАЛИСЬ, КРЫСЫ!")
        except:
            await message.answer("🎯 НЕ МОГУ ВЫБРАТЬ! ДАЙ БОЛЬШЕ ПРАВ!")
        return

    # Просто позвали Каори
    if text_lower in ["каори", "каори!", "каори?", "каори...", "каори.", "каори,"]:
        await message.answer(random_angry())
        return

    # Каори + любой текст
    if text_lower.startswith("каори ") and not text_lower.startswith("каори инфо") and not text_lower.startswith("каори инфа") and not text_lower.startswith("каори кто"):
        await message.answer(random_angry())
        return

    # ========== КОМАНДЫ ==========
    parts = text_lower.split()
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    # ========== СПИСОК КОМАНД ==========
    if cmd in ["команды", "помощь", "help", "commands", "команда"]:
        await show_commands(message)
        return

    # ========== БАЛАНС ==========
    if cmd in ["баланс", "balance", "деньги", "коины", "coins"]:
        data = get_user_data(chat_id, user_id)
        coins = data['coins']
        if coins < 100: comment = "НИЩЕБРОД! ИДИ ФАРМИ!"
        elif coins < 1000: comment = "ТАК СЕБЕ..."
        elif coins < 5000: comment = "НЕПЛОХО, НО МАЛО!"
        elif coins < 10000: comment = "БОГАЧ!"
        else: comment = "ТЫ ЧТО, БАНК ОГРАБИЛ?!"
        emoji = get_boobs_emoji(data["boobs_size"])
        await message.answer(
            f"💰 {message.from_user.full_name}\n"
            f"💎 Монеты: {coins}\n"
            f"🍒 Сиськи: {data['boobs_size']} см {emoji}\n"
            f"📊 Уровень: {data['level']}\n"
            f"💬 Сообщений: {data['msg_count']}\n"
            f"👶 Детей: {len(data['children'])}\n\n"
            f"{comment}"
        )
        return

    # ========== СИСЬКИ ==========
    if cmd in ["сиськи", "моисиськи", "грудь", "бюст", "boobs"]:
        data = get_user_data(chat_id, user_id)
        size = data["boobs_size"]
        emoji = get_boobs_emoji(size)
        if size == 0: comment = "ПЛОСКАЯ ДОСКА! НАДО КАЧАТЬ!"
        elif size < 5: comment = "МАЛЕНЬКИЕ, НО АККУРАТНЕНЬКИЕ..."
        elif size < 15: comment = "УЖЕ НЕПЛОХО! СОЧНО!"
        elif size < 30: comment = "БОЛЬШИЕ! ВСЕ ЗАВИДУЮТ!"
        elif size < 50: comment = "ОГРОМНЫЕ! ШКАФ!"
        else: comment = "ГИГАНТСКИЕ! КАК ТЫ ХОДИШЬ?!"
        await message.answer(
            f"🍒 **СИСЬКИ {message.from_user.full_name}:**\n"
            f"📏 Размер: {size} см {emoji}\n"
            f"💬 {comment}\n\n"
            f"Что бы подкачать сиськи — пиши: качать"
        )
        return

    # ========== КАЧАТЬ СИСЬКИ ==========
    if cmd in ["качать", "кач", "растить", "увеличить"]:
        data = get_user_data(chat_id, user_id)
        if random.random() < 0.6:
            growth = random.randint(1, 3)
            data["boobs_size"] += growth
            msg = random.choice(BOOBS_MESSAGES).replace("{size}", str(data["boobs_size"]))
            await message.answer(f"🍒 {msg} {get_boobs_emoji(data['boobs_size'])}")
        else:
            fails = [
                "❌ НЕ ВЫРОСЛИ... ПОПРОБУЙ ЕЩЁ!",
                "❌ СИСЬКИ НЕ ПОДДАЮТСЯ! НАВЕРНОЕ, НЕ ТВОЙ ДЕНЬ...",
                "❌ БЮСТ ОСТАЛСЯ ПРЕЖНИМ. КАЧАЙ ДАЛЬШЕ!",
                "❌ НИКАКОГО ЭФФЕКТА... МОЖЕТ, НУЖЕН МАССАЖ?",
            ]
            await message.answer(random.choice(fails))
        return

    # ========== ТОП СИСЕК ==========
    if cmd in ["топсисек", "груди", "топгрудь"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["boobs_size"], reverse=True)[:10]
        if not sorted_users:
            await message.answer("НИ У КОГО НЕТ СИСЕК! КАЧАЙТЕ!")
            return
        text_out = "🍒 **ТОП СИСЕК ЧАТА:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['boobs_size']} см {get_boobs_emoji(data['boobs_size'])}\n"
        await message.answer(text_out + "\nСИСЬКИ РЕШАЮТ!")
        return

    # ========== ТОП ПО УРОВНЯМ ==========
    if cmd in ["топ", "top", "лидеры"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["xp"] + x[1]["level"] * 150, reverse=True)[:10]
        if not sorted_users:
            await message.answer("ТУТ НИКОГО НЕТ, ВСЕ ДНИЩА!")
            return
        text_out = "🏆 **ТОП ЧАТА:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — Ур.{data['level']} | {get_rank_name(data['level'])}\n"
        await message.answer(text_out + "\nНО ВЫ ВСЁ РАВНО ВСЕ ОТСТОЙ! 😂")
        return

    # ========== ТОП БОГАЧЕЙ ==========
    if cmd in ["богачи", "топбогачей", "rich"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]
        if not sorted_users:
            await message.answer("ВСЕ НИЩИЕ! НЕТ БОГАЧЕЙ!")
            return
        text_out = "💰 **ТОП БОГАЧЕЙ:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['coins']} 💎\n"
        await message.answer(text_out)
        return

    # ========== СТАТА ==========
    if cmd in ["стата", "статистика", "stat"]:
        if args and args[0] == "я":
            data = get_user_data(chat_id, user_id)
            await message.answer(
                f"📊 **ТВОЯ СТАТИСТИКА:**\n\n"
                f"💬 Сообщений: {data['msg_count']}\n"
                f"📈 Уровень: {data['level']}\n"
                f"💰 Монет: {data['coins']} 💎\n"
                f"🍒 Сиськи: {data['boobs_size']} см\n"
                f"👶 Детей: {len(data['children'])}"
            )
            return

        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["msg_count"], reverse=True)[:15]
        if not sorted_users:
            await message.answer("СТАТИСТИКИ ПОКА НЕТ!")
            return
        text_out = "💬 **ТОП БОЛТУНОВ:**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 12
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — {data['msg_count']} сообщ.\n"
        await message.answer(text_out + "\nМЕНЬШЕ БОЛТАЙТЕ, БОЛЬШЕ ДЕЛАЙТЕ!")
        return

    # ========== СПИСОК БРАКОВ ==========
    if cmd in ["браки", "пары", "семьи", "marriages"]:
        if chat_id not in marriages or not marriages[chat_id]:
            await message.answer("💔 В ЧАТЕ ЕЩЁ НЕТ БРАКОВ! ВСЕ ОДИНОКИЕ ПРИДУРКИ!")
            return
        text_out = "💍 **БРАКИ В ЧАТЕ:**\n\n"
        for i, (u1, u2, date) in enumerate(marriages[chat_id], 1):
            name1 = await get_user_name(chat_id, u1)
            name2 = await get_user_name(chat_id, u2)
            days = (datetime.now() - date).days
            text_out += f"{i}. {name1} 💞 {name2} — {days} дн.\n"
        text_out += f"\nВСЕГО ПАР: {len(marriages[chat_id])}"
        await message.answer(text_out)
        return

    # ========== ФАРМ ==========
    if cmd in ["фарма", "work", "работа", "фарм"]:
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_work"] and (now - data["last_work"]).seconds < 1800:
            remaining = 1800 - (now - data["last_work"]).seconds
            mins, secs = remaining // 60, remaining % 60
            await message.answer(f"⏰ ТЫ УЖЕ РАБОТАЛ! ЖДИ {mins} МИН {secs} СЕК, ЛЕНТЯЙ!")
            return
        jobs = [
            "РАЗГРУЖАЛ ФУРЫ С ДЕРЬМОМ", "МЫЛ ПОЛЫ В ОБЩЕСТВЕННОМ ТУАЛЕТЕ",
            "РАБОТАЛ СТРИПТИЗЁРОМ ДЛЯ БАБУШЕК", "ПРОДАЛ ПОЧКУ НА ЧЁРНОМ РЫНКЕ",
            "ТАНЦЕВАЛ НА КАМЕРУ ДЛЯ ИЗВРАЩЕНЦЕВ", "ГРУЗИЛ МЕШКИ С ЦЕМЕНТОМ",
        ]
        job = random.choice(jobs)
        earned = random.randint(50, 300)
        bonus = 0
        if random.random() < 0.1:
            bonus = random.randint(100, 500)
            earned += bonus
        data["coins"] += earned
        data["last_work"] = now
        text_out = f"💼 ТЫ {job} И ЗАРАБОТАЛ {earned} 💎!"
        if bonus: text_out += f"\n🎉 ОГО! ПРЕМИЯ {bonus} 💎!"
        await message.answer(text_out)
        return

    # ========== БОНУС ==========
    if cmd in ["бонус", "daily", "награда"]:
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_daily"] and (now - data["last_daily"]).days < 1:
            next_time = data["last_daily"] + timedelta(days=1)
            remaining = next_time - now
            hours, mins = remaining.seconds // 3600, (remaining.seconds % 3600) // 60
            await message.answer(f"⏰ БОНУС БУДЕТ ЧЕРЕЗ {hours} Ч {mins} МИН, ЖАДИНА!")
            return
        bonus_coins = random.randint(200, 1000)
        data["coins"] += bonus_coins
        data["last_daily"] = now
        await message.answer(f"🎁 ЕЖЕДНЕВНЫЙ БОНУС: {bonus_coins} 💎!")
        return

    # ========== ПЕРЕВОД ==========
    if cmd in ["перевод", "pay", "перевести", "дать"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА СООБЩЕНИЕ ТОГО, КОМУ ПЕРЕВОДИШЬ!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СКОЛЬКО? Например: перевод 100")
            return
        amount = int(args[0])
        if amount <= 0:
            await message.answer("СУММА ДОЛЖНА БЫТЬ БОЛЬШЕ НУЛЯ!")
            return
        data = get_user_data(chat_id, user_id)
        if data["coins"] < amount:
            await message.answer(f"НЕТ СТОЛЬКО! У ТЕБЯ {data['coins']} 💎")
            return
        target_id = message.reply_to_message.from_user.id
        target = get_user_data(chat_id, target_id)
        data["coins"] -= amount
        target["coins"] += amount
        target_name = await get_user_name(chat_id, target_id)
        await message.answer(f"💸 {message.from_user.full_name} ПЕРЕВЁЛ {amount} 💎 {target_name}!")
        return

    # ========== БРАК ==========
    if cmd in ["брак", "marry", "жениться"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, С КЕМ ХОЧЕШЬ В БРАК!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if user_id == target_id:
            await message.answer("НА СЕБЕ НЕЛЬЗЯ, ШИЗОФРЕНИК!")
            return
        data = get_user_data(chat_id, user_id)
        target = get_user_data(chat_id, target_id)
        if data["married_to"]:
            await message.answer("ТЫ УЖЕ В БРАКЕ! СНАЧАЛА РАЗВЕДИСЬ!")
            return
        if target["married_to"]:
            await message.answer(f"{target_name} УЖЕ ЗАНЯТ(А)!")
            return
        await message.answer(
            f"💍 {target_name}, {message.from_user.full_name} ПРЕДЛАГАЕТ БРАК!",
            reply_markup=marriage_keyboard(user_id, target_id)
        )
        return

    # ========== РАЗВОД ==========
    if cmd in ["развод", "divorce", "развестись"]:
        data = get_user_data(chat_id, user_id)
        if not data["married_to"]:
            await message.answer("ТЫ НЕ В БРАКЕ, ОДИНОКИЙ ПРИДУРОК!")
            return
        penalty = 500
        if data["coins"] < penalty:
            await message.answer(f"НА РАЗВОД НУЖНО {penalty} 💎!")
            return
        partner_id = data["married_to"]
        partner = get_user_data(chat_id, partner_id)
        partner_name = await get_user_name(chat_id, partner_id)
        data["coins"] -= penalty
        data["married_to"] = None
        partner["married_to"] = None
        children_to_keep = [c for c in data["children"] if random.random() < 0.5]
        for c in data["children"]:
            if c not in children_to_keep and c in partner["children"]:
                partner["children"].remove(c)
        data["children"] = children_to_keep
        if chat_id in marriages:
            marriages[chat_id] = [(u1, u2, d) for u1, u2, d in marriages[chat_id] if not (u1 == user_id or u2 == user_id)]
        await message.answer(f"💔 {message.from_user.full_name} РАЗВЁЛСЯ С {partner_name}! ШТРАФ {penalty} 💎")
        return

    # ========== ДЕТИ ==========
    if cmd in ["дети", "children", "моидети"]:
        data = get_user_data(chat_id, user_id)
        if not data["children"]:
            await message.answer("👶 У ТЕБЯ НЕТ ДЕТЕЙ! ЗАВЕДИ ЧЕРЕЗ СЕКС ИЛИ УСЫНОВИ!")
            return
        text_out = "👶 **ТВОИ ДЕТИ:**\n\n"
        for i, child_id in enumerate(data["children"], 1):
            if isinstance(child_id, int):
                name = await get_user_name(chat_id, child_id)
            else:
                name = child_id
            text_out += f"{i}. {name}\n"
        await message.answer(text_out)
        return

    # ========== УСЫНОВИТЬ ==========
    if cmd in ["усыновить", "adopt"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОГО УСЫНОВИТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if user_id == target_id:
            await message.answer("СЕБЯ НЕЛЬЗЯ!")
            return
        data = get_user_data(chat_id, user_id)
        cost = 300
        if data["coins"] < cost:
            await message.answer(f"УСЫНОВЛЕНИЕ СТОИТ {cost} 💎!")
            return
        if target_id in data["children"]:
            await message.answer("ОН(А) УЖЕ ТВОЙ РЕБЁНОК!")
            return
        if len(data["children"]) >= 10:
            await message.answer("У ТЕБЯ УЖЕ 10 ДЕТЕЙ! КУДА СТОЛЬКО?")
            return
        data["coins"] -= cost
        data["children"].append(target_id)
        await message.answer(f"👶 {target_name} ТЕПЕРЬ ТВОЙ РЕБЁНОК! -{cost} 💎")
        return

    # ========== ОТКАЗ ОТ РЕБЁНКА ==========
    if cmd in ["отказ", "abandon"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА РЕБЁНКА!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        data = get_user_data(chat_id, user_id)
        if target_id not in data["children"]:
            await message.answer("ЭТО НЕ ТВОЙ РЕБЁНОК!")
            return
        data["children"].remove(target_id)
        await message.answer(f"💔 {target_name} БОЛЬШЕ НЕ ТВОЙ РЕБЁНОК! МОНСТР!")
        return

    # ========== СЕКС ==========
    if cmd in ["секс", "sex", "трах", "ебать"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, С КЕМ ХОЧЕШЬ ЗАНЯТЬСЯ СЕКСОМ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if user_id == target_id:
            await message.answer("САМ С СОБОЙ? ИДИ ЛУЧШЕ ПОДРОЧИ!")
            return
        data = get_user_data(chat_id, user_id)
        now = datetime.now()
        if data["last_sex"] and (now - data["last_sex"]).seconds < 600:
            remaining = 600 - (now - data["last_sex"]).seconds
            mins, secs = remaining // 60, remaining % 60
            await message.answer(f"⏰ ТЫ ТОЛЬКО ЧТО ТРАХАЛСЯ! ОТДОХНИ {mins} МИН {secs} СЕК!")
            return
        data["last_sex"] = now
        if random.random() < 0.7:
            msg = random.choice(SEX_MESSAGES).replace("{partner}", target_name)
            if random.random() < 0.3:
                baby_name = random.choice(BABY_NAMES)
                data["children"].append(f"👶{baby_name}")
                msg += f"\n\n🎉 И ВЫ ЗАЧАЛИ РЕБЁНКА! ЕГО БУДУТ ЗВАТЬ **{baby_name}**!"
            else:
                msg += "\n\n😏 БЕЗ ПОСЛЕДСТВИЙ... НА ЭТОТ РАЗ."
            await message.answer(f"🔥 {msg}")
        else:
            msg = random.choice(SEX_FAIL_MESSAGES).replace("{partner}", target_name)
            await message.answer(f"❌ {msg}")
        return

    # ========== ОТЛИЗ ==========
    if cmd in ["отлиз", "lick", "лизать", "отлизать", "полизать"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОГО ХОЧЕШЬ ОТЛИЗАТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        data = get_user_data(chat_id, user_id)
        now = datetime.now()

        # Кулдаун 5 минут
        if data["last_lick"] and (now - data["last_lick"]).seconds < 300:
            remaining = 300 - (now - data["last_lick"]).seconds
            mins, secs = remaining // 60, remaining % 60
            await message.answer(f"⏰ ЯЗЫК УСТАЛ! ОТДОХНИ {mins} МИН {secs} СЕК!")
            return

        data["last_lick"] = now
        licker_name = message.from_user.full_name

        if user_id == target_id:
            msg = random.choice(LICK_SELF_MESSAGES).replace("{licker}", licker_name)
        else:
            msg = random.choice(LICK_MESSAGES).replace("{licker}", licker_name).replace("{target}", target_name)

        await message.answer(f"👅 {msg}")
        return

    # ========== МАГАЗИН ==========
    SHOP_ITEMS = [
        {"name": "🎭 СМЕНА РАНГА", "desc": "Сменит название ранга", "cost": 1000},
        {"name": "💎 УДВОЕНИЕ XP", "desc": "Двойной XP на 1 час", "cost": 500},
        {"name": "🍒 БУСТЕР СИСЕК", "desc": "+5 см к сиськам мгновенно", "cost": 1500},
        {"name": "💖 СВИДАНИЕ С КАОРИ", "desc": "Особое сообщение от Каори", "cost": 2000},
        {"name": "🎰 ЛАКИ-БУСТ", "desc": "+20% к выигрышу в казино", "cost": 800},
        {"name": "💰 УДВОЕНИЕ ФАРМА", "desc": "Двойной доход с работы", "cost": 600},
        {"name": "👶 УСКОРИТЕЛЬ ДЕТЕЙ", "desc": "Следующий секс 100% ребёнок", "cost": 1200},
        {"name": "🎩 VIP-СТАТУС", "desc": "Особая отметка в топе", "cost": 5000},
    ]

    if cmd in ["магаз", "shop", "магазин"]:
        text_out = "🛒 **МАГАЗИН КАОРИ:**\n\n"
        for i, item in enumerate(SHOP_ITEMS, 1):
            text_out += f"{i}. {item['name']} — {item['cost']} 💎\n   _{item['desc']}_\n\n"
        text_out += "КУПИТЬ: купить [номер]"
        await message.answer(text_out)
        return

    if cmd in ["купить", "buy"]:
        if not args or not args[0].isdigit():
            await message.answer("ЧТО ПОКУПАТЬ? купить 1")
            return
        index = int(args[0]) - 1
        if index < 0 or index >= len(SHOP_ITEMS):
            await message.answer("НЕТ ТАКОГО ТОВАРА!")
            return
        item = SHOP_ITEMS[index]
        data = get_user_data(chat_id, user_id)
        if data["coins"] < item["cost"]:
            await message.answer(f"НЕ ХВАТАЕТ! НУЖНО {item['cost']} 💎, У ТЕБЯ {data['coins']} 💎")
            return
        data["coins"] -= item["cost"]
        if item["name"] == "🍒 БУСТЕР СИСЕК":
            data["boobs_size"] += 5
            await message.answer(f"🍒 СИСЬКИ +5 см! Теперь {data['boobs_size']} см {get_boobs_emoji(data['boobs_size'])}!")
        elif item["name"] == "💖 СВИДАНИЕ С КАОРИ":
            await message.answer(f"💖 {message.from_user.full_name}, ТЫ КУПИЛ СВИДАНИЕ СО МНОЙ... ЛАДНО, ТАК УЖ И БЫТЬ, ТЫ МНЕ НЕМНОГО НРАВИШЬСЯ! 😳💕")
        else:
            await message.answer(f"✅ КУПЛЕНО: {item['name']} ЗА {item['cost']} 💎!")
        return

    # ========== ДУЭЛЬ ==========
    if cmd in ["дуэль", "duel"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, С КЕМ ДРАТЬСЯ!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СТАВКА? дуэль 100")
            return
        bet = int(args[0])
        if bet < 10:
            await message.answer("МИНИМАЛЬНАЯ СТАВКА 10 💎!")
            return
        target_id = message.reply_to_message.from_user.id
        data = get_user_data(chat_id, user_id)
        target = get_user_data(chat_id, target_id)
        if data["coins"] < bet or target["coins"] < bet:
            await message.answer("У КОГО-ТО НЕТ СТОЛЬКО!")
            return
        winner = random.choice([user_id, target_id])
        loser = target_id if winner == user_id else user_id
        get_user_data(chat_id, winner)["coins"] += bet
        get_user_data(chat_id, loser)["coins"] -= bet
        w_name = await get_user_name(chat_id, winner)
        l_name = await get_user_name(chat_id, loser)
        await message.answer(f"⚔ {w_name} ПОБЕДИЛ {l_name} И ЗАБРАЛ {bet} 💎!")
        return

    # ========== СЛОТЫ ==========
    if cmd in ["слоты", "slots"]:
        if not args or not args[0].isdigit():
            await message.answer("СТАВКА? слоты 100")
            return
        bet = int(args[0])
        if bet < 10:
            await message.answer("МИНИМАЛЬНАЯ СТАВКА 10 💎!")
            return
        data = get_user_data(chat_id, user_id)
        if data["coins"] < bet:
            await message.answer(f"НЕТ ДЕНЕГ! У ТЕБЯ {data['coins']} 💎")
            return
        emojis = ["🍒", "🍋", "🔔", "💎", "7️⃣", "🍀", "⭐", "👑"]
        slot = [random.choice(emojis) for _ in range(3)]
        result = " | ".join(slot)
        if slot[0] == slot[1] == slot[2]:
            win = bet * random.choice([5, 7, 10])
            data["coins"] += win
            text_out = f"🎰 {result}\n🔥 ДЖЕКПОТ! ВЫИГРЫШ: {win} 💎!"
        elif slot[0] == slot[1] or slot[1] == slot[2] or slot[0] == slot[2]:
            win = bet * 2
            data["coins"] += win
            text_out = f"🎰 {result}\n👍 ДВЕ ПАРЫ! ВЫИГРЫШ: {win} 💎!"
        else:
            data["coins"] -= bet
            text_out = f"🎰 {result}\n👎 ПРОИГРЫШ: {bet} 💎!"
        await message.answer(text_out)
        return

    # ========== МОНЕТКА ==========
    if cmd in ["монетка", "coinflip"]:
        if len(args) < 2 or not args[0].isdigit():
            await message.answer("СТАВКА И ВЫБОР! монетка 100 орел")
            return
        bet = int(args[0])
        if bet < 10:
            await message.answer("МИНИМАЛЬНАЯ СТАВКА 10 💎!")
            return
        choice = args[1].lower().replace("ё", "е")
        if choice == "орёл": choice = "орел"
        data = get_user_data(chat_id, user_id)
        if data["coins"] < bet:
            await message.answer("НЕТ ДЕНЕГ!")
            return
        if choice not in ["орел", "решка"]:
            await message.answer("ОРЕЛ ИЛИ РЕШКА!")
            return
        coin = random.choice(["орел", "решка"])
        if choice == coin:
            data["coins"] += bet
            await message.answer(f"🪙 {coin.upper()}! ВЫИГРЫШ: {bet} 💎!")
        else:
            data["coins"] -= bet
            await message.answer(f"🪙 {coin.upper()}! ПРОИГРЫШ: {bet} 💎!")
        return

    # ========== КРАЖА ==========
    if cmd in ["кража", "steal", "украсть"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ЖЕРТВУ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if user_id == target_id:
            await message.answer("СЕБЯ НЕЛЬЗЯ!")
            return
        data = get_user_data(chat_id, user_id)
        target = get_user_data(chat_id, target_id)
        if target["coins"] < 50:
            await message.answer("У ЖЕРТВЫ НЕТ ДЕНЕГ!")
            return
        if random.random() < 0.4:
            stolen = min(random.randint(10, 300), target["coins"])
            target["coins"] -= stolen
            data["coins"] += stolen
            await message.answer(f"🦹 ТЫ УКРАЛ {stolen} 💎 У {target_name}!")
        else:
            penalty = random.randint(50, 300)
            if data["coins"] >= penalty:
                data["coins"] -= penalty
                target["coins"] += penalty
            await message.answer(f"🚨 ПОПАЛСЯ! ШТРАФ {penalty} 💎!")
        return

    # ========== РУЛЕТКА ==========
    if cmd in ["рулетка", "roulette"]:
        if not args or not args[0].isdigit():
            await message.answer("СТАВКА? рулетка 100")
            return
        bet = int(args[0])
        if bet < 10:
            await message.answer("МИНИМАЛЬНАЯ СТАВКА 10 💎!")
            return
        data = get_user_data(chat_id, user_id)
        if data["coins"] < bet:
            await message.answer(f"НЕТ ДЕНЕГ! У ТЕБЯ {data['coins']} 💎")
            return
        bullet = random.randint(1, 6)
        if bullet == 1:
            loss = bet * 3
            if data["coins"] >= loss:
                data["coins"] -= loss
                await message.answer(f"🔫 БАХ! ПРОИГРЫШ: {loss} 💎!")
            else:
                data["coins"] = 0
                await message.answer(f"🔫 БАХ! ТЫ ПРОИГРАЛ ВСЁ! 0 💎...")
        else:
            win = bet * 2
            data["coins"] += win
            await message.answer(f"🔫 ПРОНЕСЛО! ВЫИГРЫШ: {win} 💎!")
        return

    # ========== СЧЁТЧИК СООБЩЕНИЙ + XP ==========
    data = get_user_data(chat_id, user_id)
    data["msg_count"] += 1
    data["xp"] += random.randint(1, 5)
    needed = get_level_xp_needed(data["level"])
    if data["xp"] >= needed:
        data["level"] += 1
        data["xp"] -= needed
        await message.answer(
            f"⬆ {message.from_user.full_name} ДОСТИГ УРОВНЯ {data['level']}!\n"
            f"🏅 НОВЫЙ РАНГ: {get_rank_name(data['level'])}!"
        )

# ================== ПОКАЗАТЬ КОМАНДЫ ==================
async def show_commands(message: types.Message):
    await message.answer(
        """😤 **КОМАНДЫ КАОРИ:**

🗣 **ОБРАЩЕНИЯ:**
Каори — позвать
Каори инфа [вопрос] — процент
Каори кто [текст] — случайный чел

💰 **ЭКОНОМИКА:**
фарма — работать
бонус — ежедневный бонус
баланс — баланс и стата
перевод 100 — перевести (reply)
топ — топ по уровням
богачи — топ богачей

💍 **ОТНОШЕНИЯ:**
брак — предложить (reply)
развод — развестись (500 💎)
браки — список пар
секс — заняться сексом (reply)
дети — твои дети
усыновить — усыновить (reply, 300 💎)
отказ — отказаться от ребёнка (reply)

👅 **ОТЛИЗ:**
отлиз — отлизать кого-то (reply)

🍒 **СИСЬКИ:**
сиськи — посмотреть размер
качать — увеличить
топсисек — топ грудей

🛒 **МАГАЗИН:**
магаз — магазин
купить 1 — купить

🎰 **КАЗИНО:**
дуэль 100 — дуэль (reply)
слоты 100 — слоты
монетка 100 орел — орёл/решка
рулетка 100 — рулетка (x2/-x3)
кража — украсть (reply)

📊 **СТАТИСТИКА:**
стата — топ болтунов
стата я — моя статистика
команды — этот список
"""
    )

# ================== CALLBACK ДЛЯ БРАКА ==================
@dp.callback_query(lambda c: c.data.startswith("marry_"))
async def marry_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    parts = callback.data.split("_")
    action = parts[1]
    user1_id = int(parts[2])
    user2_id = int(parts[3])

    if callback.from_user.id != user2_id:
        await callback.answer("ЭТО НЕ ТЕБЕ ПРЕДЛАГАЛИ!", show_alert=True)
        return

    if action == "decline":
        await callback.message.edit_text("💔 БРАК ОТКЛОНЁН!")
        await callback.answer()
        return

    user1 = get_user_data(chat_id, user1_id)
    user2 = get_user_data(chat_id, user2_id)

    if user1["married_to"] or user2["married_to"]:
        await callback.message.edit_text("💔 КТО-ТО УЖЕ В БРАКЕ!")
        await callback.answer()
        return

    user1["married_to"] = user2_id
    user2["married_to"] = user1_id

    if chat_id not in marriages:
        marriages[chat_id] = []
    marriages[chat_id].append((user1_id, user2_id, datetime.now()))

    name1 = await get_user_name(chat_id, user1_id)
    name2 = await get_user_name(chat_id, user2_id)
    await callback.message.edit_text(f"💒 {name1} И {name2} ТЕПЕРЬ В БРАКЕ! 🎉")
    await callback.answer()

# ================== ЗАПУСК ==================
async def main():
    print(f"😡 {BOT_NAME} ЗАПУЩЕНА! ВСЕМ ПИЗДЕЦ!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
