# ⚠️ PRO MAX BOT (БОЛЬШОЙ КОД)

import asyncio
import json
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import *
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"
ADMIN_ID = 8250753514

PRIVATE_CHAT_ID = -1003763565634
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"
SCREEN_GROUP_ID = -1003421192077

DATA_FILE = "db.json"
LOG_FILE = "logs.txt"

bot = Bot(TOKEN)
dp = Dispatcher()

# ===== FSM =====
class AdminStates(StatesGroup):
    broadcast = State()
    ban = State()
    unban = State()

# ===== БАЗА =====
users = {}
banned = set()
waiting_payment = set()
online = set()
payments = []
last_action = {}

# ===== ЛОГ =====
def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {text}\n")

# ===== ЗАГРУЗКА =====
def load():
    global users, banned, payments
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            data = json.load(f)
            users = data.get("users", {})
            banned = set(data.get("banned", []))
            payments = data.get("payments", [])

def save():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": users,
            "banned": list(banned),
            "payments": payments
        }, f, indent=4)

# ===== АНТИ СПАМ =====
def anti(uid):
    now = datetime.now().timestamp()
    if uid in last_action and now - last_action[uid] < 1:
        return False
    last_action[uid] = now
    return True

# ===== UI =====
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Карта", callback_data="card"),
         InlineKeyboardButton(text="💰 Крипта", callback_data="crypto")],
        [InlineKeyboardButton(text="⭐ Звезды", callback_data="stars")],
        [InlineKeyboardButton(text="💎 Донат", callback_data="donate")]
    ])

def paid_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Стата", callback_data="stats")],
        [InlineKeyboardButton(text="📈 Онлайн", callback_data="online")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")],
        [InlineKeyboardButton(text="🚫 Бан", callback_data="ban")],
        [InlineKeyboardButton(text="✅ Разбан", callback_data="unban")]
    ])

# ===== START =====
@dp.message(Command("start"))
async def start(msg: Message):
    uid = msg.from_user.id

    if uid in banned:
        return

    if not anti(uid):
        return

    online.add(uid)

    uid = str(uid)

    if uid not in users:
        users[uid] = {
            "joined": str(datetime.now()),
            "paid": False,
            "sub_until": None,
            "level": "FREE"
        }
        save()

    await msg.answer("🔥 Магазин\nВыберите оплату:", reply_markup=main_kb())

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(cb: CallbackQuery):
    await cb.message.edit_text("🔥 Магазин\nВыберите оплату:", reply_markup=main_kb())

# ===== КАРТА =====
@dp.callback_query(F.data == "card")
async def card(cb: CallbackQuery):
    await cb.message.edit_text(
        "💳 2202208290305953\n👤 Даниил С.\n\n💰 120₽",
        reply_markup=paid_kb()
    )

# ===== КРИПТА =====
@dp.callback_query(F.data == "crypto")
async def crypto(cb: CallbackQuery):
    await cb.message.edit_text(
        "💰 CryptoBot + TON",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 CryptoBot", url="http://t.me/send?start=IVjeLAEQlLzA")],
            [InlineKeyboardButton(text="📲 Tonkeeper", url="https://app.tonkeeper.com/transfer/UQDQo76coCyRrsJmrxiwakSU1765516jTjGfW7rHjHUqfHBu")],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ])
    )

# ===== ОПЛАТА =====
@dp.callback_query(F.data == "paid")
async def paid(cb: CallbackQuery):
    waiting_payment.add(cb.from_user.id)
    await cb.message.edit_text("📸 Отправь скрин оплаты")

# ===== СКРИН =====
@dp.message(F.photo)
async def photo(msg: Message):
    uid = msg.from_user.id

    if uid not in waiting_payment:
        return

    waiting_payment.remove(uid)

    await bot.send_photo(
        SCREEN_GROUP_ID,
        photo=msg.photo[-1].file_id,
        caption=f"💸 {uid}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅", callback_data=f"ok_{uid}"),
             InlineKeyboardButton(text="❌", callback_data=f"no_{uid}")]
        ])
    )

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("ok_"))
async def ok(cb: CallbackQuery):
    uid = cb.data.split("_")[1]

    users[uid]["paid"] = True
    users[uid]["level"] = "PRO"
    users[uid]["sub_until"] = str(datetime.now() + timedelta(days=30))

    payments.append({"user": uid, "date": str(datetime.now())})

    save()
    log(f"PAY {uid}")

    await bot.send_message(int(uid), f"✅ Доступ:\n{PRIVATE_LINK}")
    await cb.message.edit_caption("✅")

# ===== ПРОВЕРКА ПОДПИСКИ =====
async def sub_checker():
    while True:
        now = datetime.now()

        for uid, data in users.items():
            if data["sub_until"]:
                if datetime.fromisoformat(data["sub_until"]) < now:
                    data["paid"] = False
                    data["level"] = "FREE"

                    try:
                        await bot.ban_chat_member(PRIVATE_CHAT_ID, int(uid))
                        await bot.unban_chat_member(PRIVATE_CHAT_ID, int(uid))
                    except:
                        pass

        save()
        await asyncio.sleep(60)

# ===== JOIN =====
@dp.chat_join_request()
async def join(req: ChatJoinRequest):
    uid = str(req.from_user.id)

    if uid in users and users[uid]["paid"]:
        await bot.approve_chat_join_request(req.chat.id, req.from_user.id)

# ===== АДМИН =====
@dp.message(Command("panel"))
async def panel(msg: Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("⚙️ Панель", reply_markup=admin_kb())

@dp.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):
    await cb.message.edit_text(
        f"👥 {len(users)}\n💸 {len(payments)}",
        reply_markup=admin_kb()
    )

@dp.callback_query(F.data == "online")
async def online_users(cb: CallbackQuery):
    await cb.message.edit_text(
        f"🟢 Онлайн: {len(online)}",
        reply_markup=admin_kb()
    )

# ===== РАССЫЛКА =====
@dp.callback_query(F.data == "broadcast")
async def broadcast(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.broadcast)
    await cb.message.edit_text("Отправь сообщение")

@dp.message(AdminStates.broadcast)
async def send_all(msg: Message, state: FSMContext):
    count = 0

    for u in users:
        try:
            await bot.copy_message(u, msg.chat.id, msg.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass

    await msg.answer(f"✅ {count}")
    await state.clear()

# ===== ЗАПУСК =====
async def main():
    load()
    asyncio.create_task(sub_checker())

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except Exception as e:
            log(f"ERR {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())