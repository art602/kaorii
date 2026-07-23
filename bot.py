import asyncio
import random
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

# ================== ТОКЕН ==================
TOKEN = "8739520899:AAGJY_4dGtyUoHS80iK1uqXI29gLruGnTnQ"
BOT_NAME = "kaorii"

# ================== ХРАНИЛИЩА ==================
user_data = {}       # {chat_id: {user_id: {xp, level, coins, married_to, children, last_daily, last_work, warn_count, msg_count}}}
chat_moderators = {} # {chat_id: [user_id, user_id]}
marriages = {}       # {chat_id: [(user1_id, user2_id, date)]}

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
    "ЗАНЯТА Я! НО ТАК УЖ И БЫТЬ, ЧЁ НАДО?",
]

KAORI_INFO_TEMPLATES = [
    "📊 Инфа что {question} — {percent}%",
    "📊 Я ТУТ ПОДУМАЛА... {question} — ЭТО {percent}%",
    "📊 ПО ПРОГНОЗУ КАОРИ: {question} — {percent}%",
    "📊 МОЯ ОЦЕНКА: {question} — {percent}%, НЕ БОЛЬШЕ!",
    "📊 {question}? ХА! ДУМАЮ, {percent}%",
    "📊 ШАНС ТОГО ЧТО {question} — {percent}%",
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
            "warn_count": 0, "msg_count": 0
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

def is_moderator(chat_id, user_id):
    return chat_id in chat_moderators and user_id in chat_moderators[chat_id]

def marriage_keyboard(user1_id, user2_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💍 ДА, СОГЛАСЕН!", callback_data=f"marry_accept_{user1_id}_{user2_id}")],
        [InlineKeyboardButton(text="🚫 НЕТ, ИДИ НАХУЙ!", callback_data=f"marry_decline_{user1_id}_{user2_id}")]
    ])

async def check_moder_rights(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in ["creator", "administrator"]:
            return True
    except:
        pass
    if is_moderator(chat_id, user_id):
        return True
    return False

async def get_user_name(chat_id, user_id):
    """Получить имя пользователя без тега"""
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
        f"ДОБАВЬ МЕНЯ В ЧАТ, ДАЙ ПОЛНУЮ АДМИНКУ И НЕ БЕСИ!\n\n"
        f"🔥 ЗОВИ МЕНЯ: Каори\n"
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        """😤 **КОМАНДЫ КАОРИ:**

🗣 **ОБРАЩЕНИЯ К КАОРИ:**
Каори — поздороваться (получишь матом)
Каори инфа [вопрос] — узнай процент
Каори кто [текст] — выберет случайного

💰 **ЭКОНОМИКА:**
фарма — работать (каждые 30 мин)
бонус — ежедневный бонус
баланс — твой баланс
перевод 100 — перевести монеты (reply)
топ — топ по уровням
богачи — топ по монетам
профиль — твой профиль

💍 **БРАКИ:**
брак — предложить брак (reply)
развод — развестись
браки — список всех пар
дети — твои дети
усыновить — усыновить (reply)
отказ — отказаться от ребёнка (reply)

📊 **СТАТИСТИКА:**
стата — топ по сообщениям
стата я — моя статистика

🛒 **МАГАЗИН:**
магаз — магазин
купить 1 — купить товар

🎮 **ИГРЫ:**
дуэль 100 — дуэль (reply)
слоты 100 — слоты
монетка 100 орел — орёл/решка
кража — украсть (reply)

👮 **МОДЕРАЦИЯ (модеры):**
варн — выдать варн (reply)
варны — посмотреть варны (reply)
снять — снять варн (reply)
мут 2ч — замутить (reply)
размут — размутить (reply)
бан — забанить (reply)
разбан — разбанить (reply)
кик — кикнуть (reply)
очистка 10 — удалить сообщения
модер — назначить модера (reply)
снятьмодер — снять модера (reply)
"""
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

    # Анкуд
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

    # Каори кто [текст] - БЕЗ ТЕГА, просто имя
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
                    await message.answer(
                        f"🎯 {random_user.full_name} — {who_text}!\n"
                        f"(ТЫКНУЛА ПАЛЬЦЕМ В СЛУЧАЙНОГО ЛОХА)"
                    )
                else:
                    await message.answer(
                        f"🎯 Я ВЫБРАЛА {random_user.full_name}!\n"
                        f"(СЛУЧАЙНЫЙ ЧЕЛ ИЗ ЧАТА, ХА-ХА!)"
                    )
            else:
                await message.answer("🎯 НИКОГО НЕ НАШЛА! ВСЕ РАЗБЕЖАЛИСЬ, КРЫСЫ!")
        except:
            await message.answer("🎯 НЕ МОГУ ВЫБРАТЬ! ДАЙ БОЛЬШЕ ПРАВ!")
        return

    # Просто позвали Каори
    if text_lower in ["каори", "каори!", "каори?", "каори...", "каори.", "каори,"]:
        await message.answer(random_angry())
        return

    # Каори + любой текст (кроме инфо и кто)
    if text_lower.startswith("каори ") and not text_lower.startswith("каори инфо") and not text_lower.startswith("каори инфа") and not text_lower.startswith("каори кто"):
        await message.answer(random_angry())
        return

    # ========== КОМАНДЫ БЕЗ СЛЕША ==========
    parts = text_lower.split()
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    # ========== ПРОФИЛЬ ==========
    if cmd in ["профиль", "profile", "me", "я"]:
        data = get_user_data(chat_id, user_id)
        name = message.from_user.full_name
        married_to_name = "Никто"
        if data["married_to"]:
            married_to_name = await get_user_name(chat_id, data["married_to"])
        children_count = len(data["children"])
        rank = get_rank_name(data["level"])
        text_out = (
            f"👤 **{name}**\n\n"
            f"📊 Уровень: {data['level']} ({data['xp']}/{get_level_xp_needed(data['level'])} XP)\n"
            f"🏅 Ранг: {rank}\n"
            f"💰 Монеты: {data['coins']} 💎\n"
            f"💬 Сообщений: {data['msg_count']}\n"
            f"💍 В браке с: {married_to_name}\n"
            f"👶 Детей: {children_count}\n"
            f"⚠ Варны: {data['warn_count']}/3\n"
        )
        await message.answer(text_out)
        return

    # ========== БАЛАНС ==========
    if cmd in ["баланс", "balance", "деньги", "коины", "coins"]:
        data = get_user_data(chat_id, user_id)
        coins = data['coins']
        if coins < 100:
            comment = "НИЩЕБРОД! ИДИ ФАРМИ!"
        elif coins < 1000:
            comment = "ТАК СЕБЕ..."
        elif coins < 5000:
            comment = "НЕПЛОХО, НО МАЛО!"
        elif coins < 10000:
            comment = "БОГАЧ!"
        else:
            comment = "ТЫ ЧТО, БАНК ОГРАБИЛ?!"
        await message.answer(f"💰 {message.from_user.full_name}, у тебя {coins} 💎! {comment}")
        return

    # ========== ТОП ПО УРОВНЯМ ==========
    if cmd in ["топ", "top", "лидеры"]:
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["xp"] + x[1]["level"] * 150, reverse=True)[:10]
        if not sorted_users:
            await message.answer("ТУТ НИКОГО НЕТ, ВСЕ ДНИЩА!")
            return
        text_out = "🏆 **ТОП ЧАТА (ПО УРОВНЯМ):**\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫"] * 7
        for i, (uid, data) in enumerate(sorted_users, 1):
            name = await get_user_name(chat_id, uid)
            text_out += f"{medals[i-1]} {name} — Ур.{data['level']} | {get_rank_name(data['level'])}\n"
        await message.answer(text_out + "\nНО ВЫ ВСЁ РАВНО ВСЕ ОТСТОЙ! 😂")
        return

    # ========== ТОП БОГАЧЕЙ ==========
    if cmd in ["богачи", "топбогачей", "rich", "монеты"]:
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

    # ========== СТАТА (ТОП ПО СООБЩЕНИЯМ) ==========
    if cmd in ["стата", "статистика", "stat", "сообщения"]:
        # стата я — личная статистика
        if args and args[0] == "я":
            data = get_user_data(chat_id, user_id)
            await message.answer(
                f"📊 **ТВОЯ СТАТИСТИКА:**\n\n"
                f"💬 Сообщений: {data['msg_count']}\n"
                f"📈 Уровень: {data['level']}\n"
                f"💰 Монет: {data['coins']} 💎\n"
                f"⚠ Варнов: {data['warn_count']}/3"
            )
            return

        # Общий топ по сообщениям
        users = user_data.get(chat_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1]["msg_count"], reverse=True)[:15]
        if not sorted_users:
            await message.answer("СТАТИСТИКИ ПОКА НЕТ! ПИШИТЕ БОЛЬШЕ!")
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
            "РАБОТАЛ СТРИПТИЗЁРОМ ДЛЯ БАБУШЕК", "ПЕРЕВОДИЛ БАБУШЕК ЧЕРЕЗ ДОРОГУ",
            "ПРОДАЛ ПОЧКУ НА ЧЁРНОМ РЫНКЕ", "ТАНЦЕВАЛ НА КАМЕРУ ДЛЯ ИЗВРАЩЕНЦЕВ",
            "ВЫГРЕБАЛ МУСОР ИЗ КАНАЛИЗАЦИИ", "БЫЛ ПОДОПЫТНЫМ КРОЛИКОМ",
            "ГРУЗИЛ МЕШКИ С ЦЕМЕНТОМ", "РАЗДАВАЛ ЛИСТОВКИ НА МОРОЗЕ",
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
        if bonus:
            text_out += f"\n🎉 ОГО! ПРЕМИЯ {bonus} 💎!"
        await message.answer(text_out)
        return

    # ========== БОНУС ==========
    if cmd in ["бонус", "daily", "ежедневный", "награда"]:
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
        await message.answer(f"🎁 ЕЖЕДНЕВНЫЙ БОНУС: {bonus_coins} 💎! НЕ ПРОСРИ ВСЁ СРАЗУ!")
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
            await message.answer(f"НЕТ СТОЛЬКО! У ТЕБЯ {data['coins']} 💎, НИЩЕБРОД!")
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
            f"💍 {target_name}, {message.from_user.full_name} ПРЕДЛАГАЕТ ТЕБЕ БРАК!\n"
            f"СОГЛАСЕН(НА)?",
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
            await message.answer(f"НА РАЗВОД НУЖНО {penalty} 💎! ЖИВИ С НИМ(НЕЙ) ДАЛЬШЕ!")
            return
        partner_id = data["married_to"]
        partner = get_user_data(chat_id, partner_id)
        partner_name = await get_user_name(chat_id, partner_id)
        data["coins"] -= penalty
        data["married_to"] = None
        partner["married_to"] = None
        # Делим детей
        children_to_keep = [c for c in data["children"] if random.random() < 0.5]
        for c in data["children"]:
            if c not in children_to_keep and c in partner["children"]:
                partner["children"].remove(c)
        data["children"] = children_to_keep
        # Удаляем из списка браков
        if chat_id in marriages:
            marriages[chat_id] = [(u1, u2, d) for u1, u2, d in marriages[chat_id] if not (u1 == user_id or u2 == user_id)]
        await message.answer(f"💔 {message.from_user.full_name} РАЗВЁЛСЯ С {partner_name}! ШТРАФ {penalty} 💎\nДЕТИ ПОДЕЛЕНЫ, ЖИЗНЬ БОЛЬ...")
        return

    # ========== ДЕТИ ==========
    if cmd in ["дети", "children", "моидети"]:
        data = get_user_data(chat_id, user_id)
        if not data["children"]:
            await message.answer("👶 У ТЕБЯ НЕТ ДЕТЕЙ! НАВЕРНОЕ, ЭТО К ЛУЧШЕМУ...")
            return
        text_out = "👶 **ТВОИ ДЕТИ:**\n\n"
        for i, child_id in enumerate(data["children"], 1):
            name = await get_user_name(chat_id, child_id)
            text_out += f"{i}. {name}\n"
        await message.answer(text_out)
        return

    # ========== УСЫНОВИТЬ ==========
    if cmd in ["усыновить", "adopt", "усыновление"]:
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
        if len(data["children"]) >= 5:
            await message.answer("У ТЕБЯ УЖЕ 5 ДЕТЕЙ! КУДА СТОЛЬКО?")
            return
        data["coins"] -= cost
        data["children"].append(target_id)
        await message.answer(f"👶 {target_name} ТЕПЕРЬ ТВОЙ РЕБЁНОК! -{cost} 💎")
        return

    # ========== ОТКАЗ ОТ РЕБЁНКА ==========
    if cmd in ["отказ", "abandon", "отказаться"]:
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

    # ========== МАГАЗИН ==========
    SHOP_ITEMS = [
        {"name": "🎭 СМЕНА РАНГА", "desc": "Сменит название ранга", "cost": 1000},
        {"name": "💎 УДВОЕНИЕ XP НА ЧАС", "desc": "Двойной XP на 1 час", "cost": 500},
        {"name": "🛡 ЗАЩИТА ОТ ВАРНА", "desc": "Один варн спишется", "cost": 800},
        {"name": "🔓 РАЗМУТ", "desc": "Размутить себя 1 раз", "cost": 1500},
        {"name": "💖 СВИДАНИЕ С КАОРИ", "desc": "Особое сообщение от Каори", "cost": 2000},
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
        if item["name"] == "💖 СВИДАНИЕ С КАОРИ":
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
        data = get_user_data(chat_id, user_id)
        if bet <= 0 or data["coins"] < bet:
            await message.answer(f"НЕТ ДЕНЕГ! У ТЕБЯ {data['coins']} 💎")
            return
        emojis = ["🍒", "🍋", "🔔", "💎", "7️⃣", "🍀"]
        slot = [random.choice(emojis) for _ in range(3)]
        result = " | ".join(slot)
        if slot[0] == slot[1] == slot[2]:
            win = bet * 5
            data["coins"] += win
            text_out = f"🎰 {result}\nДЖЕКПОТ! ВЫИГРЫШ: {win} 💎! ВЕЗУЧИЙ ЗАСРАНЕЦ!"
        elif slot[0] == slot[1] or slot[1] == slot[2] or slot[0] == slot[2]:
            win = bet * 2
            data["coins"] += win
            text_out = f"🎰 {result}\nДВЕ ПАРЫ! ВЫИГРЫШ: {win} 💎!"
        else:
            data["coins"] -= bet
            text_out = f"🎰 {result}\nПРОИГРЫШ: {bet} 💎! ХА-ХА, ЛОШАРА!"
        await message.answer(text_out)
        return

    # ========== МОНЕТКА ==========
    if cmd in ["монетка", "coinflip"]:
        if len(args) < 2 or not args[0].isdigit():
            await message.answer("СТАВКА И ВЫБОР! монетка 100 орел")
            return
        bet = int(args[0])
        choice = args[1].lower().replace("ё", "е")
        if choice == "орёл": choice = "орел"
        data = get_user_data(chat_id, user_id)
        if bet <= 0 or data["coins"] < bet:
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
    if cmd in ["кража", "steal", "украсть", "своровать"]:
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
            stolen = min(random.randint(10, 200), target["coins"])
            target["coins"] -= stolen
            data["coins"] += stolen
            await message.answer(f"🦹 ТЫ УКРАЛ {stolen} 💎 У {target_name}! ВОРЮГА!")
        else:
            penalty = random.randint(50, 200)
            if data["coins"] >= penalty:
                data["coins"] -= penalty
                target["coins"] += penalty
            await message.answer(f"🚨 ПОПАЛСЯ НА КРАЖЕ У {target_name}! ШТРАФ {penalty} 💎!")
        return

    # ========== МОДЕРАЦИЯ ==========

    # ВАРН
    if cmd in ["варн", "warn"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР! ЗАВАЛИ ЕБАЛО!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА НАРУШИТЕЛЯ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        target = get_user_data(chat_id, target_id)
        target["warn_count"] += 1
        if target["warn_count"] >= 3:
            try:
                await bot.ban_chat_member(chat_id, target_id)
                target["warn_count"] = 0
                await message.answer(f"🚫 {target_name} ЗАБАНЕН! 3 ВАРНА — ДО СВИДАНИЯ!")
            except:
                await message.answer("НЕ МОГУ ЗАБАНИТЬ! ДАЙ АДМИНКУ!")
        else:
            await message.answer(f"⚠ {target_name}, ВАРН! [{target['warn_count']}/3]\nЕЩЁ {3 - target['warn_count']} — И БАН!")
        return

    # ВАРНЫ
    if cmd in ["варны", "warns"]:
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, ЧЬИ ВАРНЫ СМОТРЕТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        target = get_user_data(chat_id, target_id)
        await message.answer(f"⚠ {target_name}: {target['warn_count']}/3 ВАРНОВ")
        return

    # СНЯТЬ ВАРН
    if cmd in ["снять", "unwarn"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, С КОГО СНЯТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        target = get_user_data(chat_id, target_id)
        if target["warn_count"] > 0:
            target["warn_count"] -= 1
            await message.answer(f"😒 {target_name}, ВАРН СНЯТ. ОСТАЛОСЬ: {target['warn_count']}/3\nНО СМОТРИ МНЕ!")
        else:
            await message.answer("У НЕГО НЕТ ВАРНОВ!")
        return

    # МУТ
    if cmd in ["мут", "mute"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ЖЕРТВУ!")
            return
        if not args:
            await message.answer("НА СКОЛЬКО? мут 30м / мут 2ч / мут 1д")
            return
        time_str = args[0]
        if time_str.endswith("м") or time_str.endswith("m"):
            multiplier = 1
        elif time_str.endswith("ч") or time_str.endswith("h"):
            multiplier = 60
        elif time_str.endswith("д") or time_str.endswith("d"):
            multiplier = 1440
        else:
            await message.answer("ФОРМАТ: 30м, 2ч, 1д")
            return
        try:
            duration = int(time_str[:-1]) * multiplier
        except:
            await message.answer("НЕВЕРНОЕ ВРЕМЯ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        until = datetime.now() + timedelta(minutes=duration)
        try:
            await bot.restrict_chat_member(chat_id, target_id, until_date=until, permissions=ChatPermissions(can_send_messages=False))
            await message.answer(f"🤐 {target_name} ЗАТКНУЛСЯ НА {time_str}! РОТ НА ЗАМОК!")
        except:
            await message.answer("НЕ МОГУ ЗАМУТИТЬ! ДАЙ АДМИНКУ!")
        return

    # РАЗМУТ
    if cmd in ["размут", "unmute"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ЗАТКНУВШЕГОСЯ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        try:
            await bot.restrict_chat_member(chat_id, target_id, until_date=None, permissions=ChatPermissions(can_send_messages=True))
            await message.answer(f"😒 {target_name} РАЗМУЧЕН. МОЖЕШЬ ОПЯТЬ ПИЗДЕТЬ. НО АККУРАТНЕЕ!")
        except:
            await message.answer("НЕ МОГУ РАЗМУТИТЬ!")
        return

    # БАН
    if cmd in ["бан", "ban"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОГО БАНИТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        try:
            await bot.ban_chat_member(chat_id, target_id)
            await message.answer(f"🚫 {target_name} ЗАБАНЕН НАХУЙ! НАВСЕГДА!")
        except:
            await message.answer("НЕ МОГУ ЗАБАНИТЬ! ДАЙ ПОЛНУЮ АДМИНКУ!")
        return

    # РАЗБАН
    if cmd in ["разбан", "unban"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
        elif args and args[0].isdigit():
            target_id = int(args[0])
        else:
            await message.answer("ОТВЕТЬ ИЛИ НАПИШИ ID!")
            return
        try:
            await bot.unban_chat_member(chat_id, target_id)
            await message.answer("😒 РАЗБАНЕН. ПУСТЬ НЕ БЕСИТ МЕНЯ БОЛЬШЕ!")
        except:
            await message.answer("НЕ МОГУ РАЗБАНИТЬ!")
        return

    # КИК
    if cmd in ["кик", "kick"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ВЫЛЕТАЮЩЕГО!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        try:
            await bot.ban_chat_member(chat_id, target_id)
            await bot.unban_chat_member(chat_id, target_id)
            await message.answer(f"👢 {target_name} КИКНУТ! ИДИ ГУЛЯЙ!")
        except:
            await message.answer("НЕ МОГУ КИКНУТЬ!")
        return

    # ОЧИСТКА
    if cmd in ["очистка", "purge", "снести"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ МОДЕРАТОР!")
            return
        if not args or not args[0].isdigit():
            await message.answer("СКОЛЬКО? очистка 10")
            return
        count = min(int(args[0]), 100)
        try:
            messages = []
            async for msg in bot.get_chat_history(chat_id, limit=count + 1):
                messages.append(msg.message_id)
            await bot.delete_messages(chat_id, messages)
            await message.answer(f"🧹 {count} СООБЩЕНИЙ УДАЛЕНО! ВОТ ТАК, БЛЯТЬ!")
        except:
            await message.answer("НЕ МОГУ УДАЛИТЬ!")
        return

    # МОДЕР
    if cmd in ["модер", "moder"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ АДМИН/МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА ТОГО, КОГО НАЗНАЧИТЬ!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if chat_id not in chat_moderators:
            chat_moderators[chat_id] = []
        if target_id in chat_moderators[chat_id]:
            await message.answer(f"{target_name} УЖЕ МОДЕРАТОР!")
            return
        chat_moderators[chat_id].append(target_id)
        await message.answer(f"👮 {target_name} ТЕПЕРЬ МОДЕРАТОР! НЕ ПОДВЕДИ, ИЛИ ПРИБЬЮ!")
        return

    # СНЯТЬ МОДЕРА
    if cmd in ["снятьмодер", "unmoder"]:
        if not await check_moder_rights(message):
            await message.answer("ТЫ НЕ АДМИН/МОДЕРАТОР!")
            return
        if not message.reply_to_message:
            await message.answer("ОТВЕТЬ НА МОДЕРАТОРА!")
            return
        target_id = message.reply_to_message.from_user.id
        target_name = await get_user_name(chat_id, target_id)
        if chat_id not in chat_moderators or target_id not in chat_moderators[chat_id]:
            await message.answer(f"{target_name} НЕ МОДЕРАТОР!")
            return
        chat_moderators[chat_id].remove(target_id)
        await message.answer(f"👋 {target_name} БОЛЬШЕ НЕ МОДЕРАТОР! СВОБОДЕН!")
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
            f"🏅 НОВЫЙ РАНГ: {get_rank_name(data['level'])}!\n"
            f"НО ТЫ ВСЁ РАВНО ДНИЩЕ, ПРОСТО ЧУТЬ МЕНЬШЕ!"
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
        await callback.answer("ЭТО НЕ ТЕБЕ ПРЕДЛАГАЛИ, ОТЪЕБИСЬ!", show_alert=True)
        return

    if action == "decline":
        await callback.message.edit_text("💔 БРАК ОТКЛОНЁН! ЖЕСТОКО, НО СПРАВЕДЛИВО!")
        await callback.answer()
        return

    user1 = get_user_data(chat_id, user1_id)
    user2 = get_user_data(chat_id, user2_id)

    if user1["married_to"] or user2["married_to"]:
        await callback.message.edit_text("💔 КТО-ТО УЖЕ В БРАКЕ! НЕЛЬЗЯ!")
        await callback.answer()
        return

    user1["married_to"] = user2_id
    user2["married_to"] = user1_id

    if chat_id not in marriages:
        marriages[chat_id] = []
    marriages[chat_id].append((user1_id, user2_id, datetime.now()))

    name1 = await get_user_name(chat_id, user1_id)
    name2 = await get_user_name(chat_id, user2_id)
    await callback.message.edit_text(f"💒 **ПОЗДРАВЛЯЮ!** {name1} И {name2} ТЕПЕРЬ В БРАКЕ!\nТЕПЕРЬ ВЫ МУЧАЕТЕ ДРУГ ДРУГА ОФИЦИАЛЬНО! 🎉")
    await callback.answer()

# ================== ЗАПУСК ==================
async def main():
    print(f"😡 {BOT_NAME} ЗАПУЩЕНА! ВСЕМ ПИЗДЕЦ!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())