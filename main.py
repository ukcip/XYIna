import asyncio
import json
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ChatJoinRequest
)
from aiogram.filters import Command

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"
ADMIN_ID = 8250753514

# ===== ГРУППЫ =====
SCREEN_GROUP_ID = -1003421192077
THREAD_ID = 2

PRIVATE_CHAT_ID = -1003763565634
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

DATA_FILE = "data.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ДАННЫЕ =====
users = set()
banned = set()
broadcast_mode = set()
waiting_payment = set()
payments = {}

# ===== СОХРАНЕНИЕ =====
def save():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": list(users),
            "banned": list(banned),
            "payments": payments
        }, f)

def load():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    users.update(data.get("users", []))
    banned.update(data.get("banned", []))
    payments.update(data.get("payments", {}))

# ===== КНОПКИ =====
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Карта", callback_data="card"),
            InlineKeyboardButton(text="💰 Крипта", callback_data="crypto")
        ],
        [
            InlineKeyboardButton(text="⭐ Звезды", callback_data="stars")
        ],
        [
            InlineKeyboardButton(text="💎 Донат", callback_data="donate")
        ]
    ])

def paid_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="a_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="a_broadcast")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="a_users")],
        [InlineKeyboardButton(text="💸 Оплаты", callback_data="a_payments")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id in banned:
        return

    users.add(message.from_user.id)
    save()

    await message.answer(
        "🔥 Добро пожаловать в магазин\n\n"
        "Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== ОПЛАТЫ =====
@dp.callback_query(F.data == "card")
async def card(callback: CallbackQuery):
    await callback.message.edit_text(
        "💳 2202208290305953\n\nПосле оплаты нажмите 👇",
        reply_markup=paid_kb()
    )

@dp.callback_query(F.data == "crypto")
async def crypto(callback: CallbackQuery):
    await callback.message.edit_text(
        "💰 http://t.me/send?start=IVWM9jtSGhiL",
        reply_markup=paid_kb()
    )

@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ 50 + 15 отправить @ukcip",
        reply_markup=paid_kb()
    )

@dp.callback_query(F.data == "donate")
async def donate(callback: CallbackQuery):
    await callback.message.edit_text(
        "💎 Донат\n2202208290305953"
    )

# ===== ОПЛАТИЛ =====
@dp.callback_query(F.data == "paid")
async def paid(callback: CallbackQuery):
    waiting_payment.add(callback.from_user.id)
    await callback.message.edit_text("📸 Отправьте скрин")

# ===== СКРИН =====
@dp.message(F.photo)
async def photo(message: Message):
    if message.from_user.id not in waiting_payment:
        return

    waiting_payment.remove(message.from_user.id)

    await message.answer("⏳ Проверка...")

    await bot.send_photo(
        SCREEN_GROUP_ID,
        message_thread_id=THREAD_ID,
        photo=message.photo[-1].file_id,
        caption=f"💸 {message.from_user.id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅", callback_data=f"ok_{message.from_user.id}"),
                InlineKeyboardButton(text="❌", callback_data=f"no_{message.from_user.id}")
            ]
        ])
    )

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("ok_"))
async def ok(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    payments[str(user_id)] = {
        "status": "paid",
        "date": str(datetime.now())
    }
    save()

    await bot.send_message(user_id, f"✅ Оплата принята\n{PRIVATE_LINK}")
    await callback.message.edit_caption("✅")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("no_"))
async def no(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Отклонено")
    await callback.message.edit_caption("❌")

# ===== АВТО-ПРИНЯТИЕ =====
@dp.chat_join_request()
async def auto_accept(request: ChatJoinRequest):
    if str(request.from_user.id) in payments:
        await bot.approve_chat_join_request(request.chat.id, request.from_user.id)

# ===== ПАНЕЛЬ =====
@dp.message(Command("panel"))
async def panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("⚙️ Панель", reply_markup=admin_kb())

# ===== СТАТА =====
@dp.callback_query(F.data == "a_stats")
async def stats(callback: CallbackQuery):
    await callback.message.edit_text(
        f"👥 {len(users)}\n💸 {len(payments)} оплат",
        reply_markup=admin_kb()
    )

# ===== РАССЫЛКА =====
@dp.callback_query(F.data == "a_broadcast")
async def broadcast(callback: CallbackQuery):
    broadcast_mode.add(callback.from_user.id)
    await callback.message.edit_text("Отправь сообщение")

@dp.message()
async def send_all(message: Message):
    if message.from_user.id not in broadcast_mode:
        return

    broadcast_mode.remove(message.from_user.id)

    for u in users:
        try:
            await bot.copy_message(u, message.chat.id, message.message_id)
        except:
            pass

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