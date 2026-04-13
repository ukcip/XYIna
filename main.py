import asyncio
import random
import string
import json
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command

# ===== НАСТРОЙКИ =====
TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"
ADMIN_ID = 8250753514
GROUP_ID = -1003763565634
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

DATA_FILE = "data.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ДАННЫЕ =====
users = set()
user_last_activity = {}
daily_stats = {}
waiting_payment = set()
broadcast_mode = set()

# ===== ЗАГРУЗКА =====
def load_data():
    global users, user_last_activity, daily_stats

    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    users.update(data.get("users", []))

    user_last_activity.update({
        int(k): datetime.fromisoformat(v)
        for k, v in data.get("activity", {}).items()
    })

    daily_stats.update(data.get("daily", {}))

# ===== СОХРАНЕНИЕ =====
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": list(users),
            "activity": {
                str(k): v.isoformat()
                for k, v in user_last_activity.items()
            },
            "daily": daily_stats
        }, f)

# ===== ТРЕКИНГ =====
def track_user(user_id):
    now = datetime.now()

    users.add(user_id)
    user_last_activity[user_id] = now

    day = now.strftime("%Y-%m-%d")
    daily_stats[day] = daily_stats.get(day, 0) + 1

    save_data()

# ===== АНИМАЦИЯ =====
async def loading(callback, text="⏳ Загрузка"):
    for i in range(3):
        try:
            await callback.message.edit_text(f"{text}{'.' * (i+1)}")
        except:
            pass
        await asyncio.sleep(0.4)

# ===== КНОПКИ =====
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Оплата картой", callback_data="card"),
            InlineKeyboardButton(text="💰 Оплата криптой", callback_data="crypto")
        ],
        [
            InlineKeyboardButton(text="⭐ Оплата звёздами", callback_data="stars")
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

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    track_user(message.from_user.id)

    await message.answer(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
        "Здесь вы можете приобрести доступ к привату💸\n\n"
        "👇 Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    track_user(callback.from_user.id)
    await loading(callback)

    await callback.message.edit_text(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
        "Здесь вы можете приобрести доступ к привату💸\n\n"
        "👇 Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== КАРТА =====
@dp.callback_query(F.data == "card")
async def card(callback: CallbackQuery):
    track_user(callback.from_user.id)
    await loading(callback)

    await callback.message.edit_text(
        "💳 Оплата картой\n\n"
        "💰 120₽\n"
        "📌 2202208290305953\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=paid_kb()
    )

# ===== КРИПТА =====
@dp.callback_query(F.data == "crypto")
async def crypto(callback: CallbackQuery):
    track_user(callback.from_user.id)
    await loading(callback)

    await callback.message.edit_text(
        "💰 Оплата криптой\n\n"
        "http://t.me/send?start=IVWM9jtSGhiL\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=paid_kb()
    )

# ===== ЗВЕЗДЫ =====
@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
    track_user(callback.from_user.id)
    await loading(callback)

    await callback.message.edit_text(
        "⭐ Оплата звёздами\n\n"
        "📌 Отправьте админу @ukcip:\n"
        "• 50 ⭐\n• 15 ⭐\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=paid_kb()
    )

# ===== ДОНАТ =====
@dp.callback_query(F.data == "donate")
async def donate(callback: CallbackQuery):
    track_user(callback.from_user.id)
    await loading(callback)

    await callback.message.edit_text(
        "💎 Донат\n\n"
        "💰 Крипта: http://t.me/send?start=IVjeLAEQlLzA\n"
        "💳 Карта: 2202208290305953",
        reply_markup=back_kb()
    )

# ===== Я ОПЛАТИЛ =====
@dp.callback_query(F.data == "paid")
async def paid(callback: CallbackQuery):
    waiting_payment.add(callback.from_user.id)

    await callback.message.edit_text(
        "📸 Отправьте скриншот оплаты\n\n"
        "⏳ После проверки вы получите доступ",
        reply_markup=back_kb()
    )

# ===== СКРИН =====
@dp.message(F.photo)
async def handle_photo(message: Message):
    if message.from_user.id not in waiting_payment:
        return

    waiting_payment.remove(message.from_user.id)

    msg = await message.answer("⏳ Обрабатываю оплату...")

    await bot.send_photo(
        GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=f"💸 Новая оплата\n👤 ID: {message.from_user.id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{message.from_user.id}")
            ]
        ])
    )

    await asyncio.sleep(2)

    await msg.edit_text(
        "⏳ Ваша оплата на рассмотрении\nОжидайте 24 часа"
    )

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(
        user_id,
        f"✅ Оплата подтверждена\n\n🔗 {PRIVATE_LINK}"
    )

    await callback.message.edit_caption("✅ Принято")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Оплата отклонена")
    await callback.message.edit_caption("❌ Отклонено")

# ===== СТАТИСТИКА =====
@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    now = datetime.now()

    total = len(users)

    active_24h = sum(
        1 for t in user_last_activity.values()
        if now - t < timedelta(hours=24)
    )

    online = sum(
        1 for t in user_last_activity.values()
        if now - t < timedelta(minutes=5)
    )

    chart = ""
    for i in range(5):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        count = daily_stats.get(day, 0)
        chart += f"{day[-5:]} | {'█'*min(count,10)} ({count})\n"

    await message.answer(
        f"📊 Статистика\n\n"
        f"👥 Всего: {total}\n"
        f"⚡ 24ч: {active_24h}\n"
        f"🟢 Онлайн: {online}\n\n"
        f"{chart}"
    )

# ===== РАССЫЛКА =====
@dp.message(Command("broadcast"))
async def broadcast_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode.add(message.from_user.id)
    await message.answer("📢 Отправь сообщение")

@dp.message(F.text)
async def broadcast_send(message: Message):
    if message.from_user.id not in broadcast_mode:
        return

    broadcast_mode.remove(message.from_user.id)

    for user_id in users:
        try:
            await bot.send_message(user_id, message.text)
            await asyncio.sleep(0.05)
        except:
            pass

    await message.answer("✅ Рассылка завершена")

# ===== ЗАПУСК =====
async def main():
    load_data()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())