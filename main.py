import asyncio
import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ChatJoinRequest
)
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"
ADMIN_ID = 8250753514

PRIVATE_CHAT_ID = -1003763565634
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"
SCREEN_GROUP_ID = -1003421192077

DATA_FILE = "db.json"

bot = Bot(TOKEN)
dp = Dispatcher()

# ===== FSM =====
class AdminStates(StatesGroup):
    broadcast = State()

# ===== ДАННЫЕ =====
users = {}
banned = set()
waiting_payment = set()
online = set()
payments = []
last_action = {}

# ===== БАЗА =====
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

# ===== АНТИСПАМ =====
def anti(uid):
    now = datetime.now().timestamp()
    if uid in last_action and now - last_action[uid] < 1:
        return False
    last_action[uid] = now
    return True

# ===== ТЕКСТ =====
MAIN_TEXT = (
    "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
    "Здесь вы можете приобрести доступ к привату💸\n\n"
    "👇 Выберите способ оплаты:"
)

# ===== КНОПКИ =====
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
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast")]
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
            "paid": False
        }
        save()

    await msg.answer(MAIN_TEXT, reply_markup=main_kb())

# ===== BACK =====
@dp.callback_query(F.data == "back")
async def back(cb: CallbackQuery):
    await cb.message.edit_text(MAIN_TEXT, reply_markup=main_kb())

# ===== КАРТА =====
@dp.callback_query(F.data == "card")
async def card(cb: CallbackQuery):
    await cb.message.edit_text(
        "💳 Оплата картой\n\n"
        "2202208290305953\n"
        "👤 Даниил С.\n\n"
        "❗ После оплаты нажмите кнопку ниже",
        reply_markup=paid_kb()
    )

# ===== КРИПТА (ТОЛЬКО CRYPTOBOT) =====
@dp.callback_query(F.data == "crypto")
async def crypto(cb: CallbackQuery):
    await cb.message.edit_text(
        "💰 Оплата криптовалютой\n\n"
        "Нажмите кнопку ниже",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 CryptoBot", url="http://t.me/send?start=IVjeLAEQlLzA")],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ])
    )

# ===== ЗВЕЗДЫ =====
@dp.callback_query(F.data == "stars")
async def stars(cb: CallbackQuery):
    await cb.message.edit_text(
        "⭐ Оплата звездами\n\n"
        "Отправьте админу @ukcip:\n"
        "50⭐ + 15⭐\n\n"
        "После оплаты нажмите кнопку ниже",
        reply_markup=paid_kb()
    )

# ===== ДОНАТ =====
@dp.callback_query(F.data == "donate")
async def donate(cb: CallbackQuery):
    await cb.message.edit_text(
        "💎 Донат\n\n"
        "💳 Карта:\n"
        "2202208290305953\n"
        "👤 Даниил С.\n\n"
        "💰 Крипта:\n"
        "через CryptoBot\n\n"
        "💎 TON:\n"
        "UQDQo76coCyRrsJmrxiwakSU1765516jTjGfW7rHjHUqfHBu",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 CryptoBot", url="http://t.me/send?start=IVjeLAEQlLzA")],
            [InlineKeyboardButton(text="📲 Tonkeeper", url="https://app.tonkeeper.com/transfer/UQDQo76coCyRrsJmrxiwakSU1765516jTjGfW7rHjHUqfHBu")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ])
    )

# ===== Я ОПЛАТИЛ =====
@dp.callback_query(F.data == "paid")
async def paid(cb: CallbackQuery):
    waiting_payment.add(cb.from_user.id)
    await cb.message.edit_text("📸 Отправьте скрин оплаты")

# ===== СКРИН =====
@dp.message(F.photo)
async def handle_payment(message: Message):
    uid = message.from_user.id

    if uid not in waiting_payment:
        return

    waiting_payment.remove(uid)

    msg = await message.answer("⏳ Обрабатываю оплату...")

    await bot.send_photo(
        SCREEN_GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=f"💸 Новая заявка\n👤 {uid}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"ok_{uid}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"no_{uid}")
            ]
        ])
    )

    await asyncio.sleep(2)

    await msg.edit_text(
        "✅ Ваша заявка отправлена на рассмотрение\n\n"
        "⏳ Ожидайте до 24 часов"
    )

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("ok_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    uid = str(user_id)

    if uid in users:
        users[uid]["paid"] = True
        payments.append({"user": uid, "date": str(datetime.now())})
        save()

    try:
        await bot.send_message(
            user_id,
            "✅ Оплата подтверждена!\n\n"
            f"🔓 Доступ:\n{PRIVATE_LINK}"
        )
    except:
        pass

    await callback.message.edit_caption(f"✅ Принято\n👤 {user_id}")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("no_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    try:
        await bot.send_message(
            user_id,
            "❌ Оплата отклонена\n\nОтправьте корректный скрин"
        )
    except:
        pass

    await callback.message.edit_caption(f"❌ Отклонено\n👤 {user_id}")

# ===== АВТО-ПРИНЯТИЕ =====
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
        f"👥 Пользователей: {len(users)}\n💸 Оплат: {len(payments)}",
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

    await msg.answer(f"✅ Отправлено: {count}")
    await state.clear()

# ===== ЗАПУСК =====
async def main():
    load()

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())