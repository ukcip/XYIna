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

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"
ADMIN_ID = 8250753514

# ===== ГРУППЫ =====
SCREEN_GROUP_ID = -1003421192077
THREAD_ID = 2

PRIVATE_CHAT_ID = -1003763565634
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

DATA_FILE = "database.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ДАННЫЕ =====
users = {}
banned = set()
waiting_payment = set()
broadcast_mode = set()

# ===== БАЗА =====
def load_data():
    global users, banned
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            users = data.get("users", {})
            banned = set(data.get("banned", []))

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": users,
            "banned": list(banned)
        }, f, indent=4)

# ===== ТЕКСТ =====
MAIN_TEXT = (
    "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
    "Здесь вы можете приобрести доступ к привату💸\n\n"
    "👇 Выберите способ оплаты:"
)

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

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="a_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="a_broadcast")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="a_users")],
        [InlineKeyboardButton(text="💸 Оплаты", callback_data="a_payments")],
        [InlineKeyboardButton(text="🚫 Бан", callback_data="a_ban")],
        [InlineKeyboardButton(text="✅ Разбан", callback_data="a_unban")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id in banned:
        return

    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "username": message.from_user.username,
            "joined": str(datetime.now()),
            "paid": False
        }
        save_data()

    await message.answer(MAIN_TEXT, reply_markup=main_kb())

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(MAIN_TEXT, reply_markup=main_kb())

# ===== ОПЛАТЫ =====
@dp.callback_query(F.data == "card")
async def card(callback: CallbackQuery):
    await callback.message.edit_text(
        "💳 Оплата картой\n\n"
        "💰 Сумма: 120₽\n"
        "📌 Реквизиты:\n"
        "2202208290305953\n\n"
        "❗ После оплаты нажмите кнопку ниже",
        reply_markup=paid_kb()
    )

@dp.callback_query(F.data == "crypto")
async def crypto(callback: CallbackQuery):
    await callback.message.edit_text(
        "💰 Оплата криптовалютой\n\n"
        "🔗 Перейдите по ссылке:\n"
        "http://t.me/send?start=IVWM9jtSGhiL\n\n"
        "❗ После оплаты нажмите кнопку ниже",
        reply_markup=paid_kb()
    )

@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ Оплата звёздами\n\n"
        "Отправьте админу @ukcip:\n"
        "• 50⭐\n"
        "• затем 15⭐\n\n"
        "⏳ После оплаты нажмите кнопку ниже",
        reply_markup=paid_kb()
    )

@dp.callback_query(F.data == "donate")
async def donate(callback: CallbackQuery):
    await callback.message.edit_text(
        "💎 Донат\n\n"
        "💳 Карта:\n"
        "2202208290305953\n\n"
        "💰 Крипта:\n"
        "http://t.me/send?start=IVjeLAEQlLzA",
        reply_markup=back_kb()
    )

# ===== ОПЛАТИЛ =====
@dp.callback_query(F.data == "paid")
async def paid(callback: CallbackQuery):
    waiting_payment.add(callback.from_user.id)
    await callback.message.edit_text("📸 Отправьте скриншот оплаты")

# ===== СКРИН =====
@dp.message(F.photo)
async def handle_photo(message: Message):
    if message.from_user.id not in waiting_payment:
        return

    waiting_payment.remove(message.from_user.id)

    msg = await message.answer("⏳ Обрабатываю оплату...")

    await bot.send_photo(
        chat_id=SCREEN_GROUP_ID,
        message_thread_id=THREAD_ID,
        photo=message.photo[-1].file_id,
        caption=f"💸 Новая оплата\n👤 {message.from_user.id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{message.from_user.id}")
            ]
        ])
    )

    await asyncio.sleep(2)
    await msg.edit_text("⏳ Оплата на проверке (до 24ч)")

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]

    if user_id in users:
        users[user_id]["paid"] = True
        save_data()

    await bot.send_message(
        int(user_id),
        f"✅ Оплата подтверждена!\n\n{PRIVATE_LINK}\n\nПодайте заявку"
    )

    await callback.message.edit_caption("✅ Принято")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Оплата отклонена")
    await callback.message.edit_caption("❌ Отклонено")

# ===== АВТО-ПРИНЯТИЕ =====
@dp.chat_join_request()
async def auto_accept(request: ChatJoinRequest):
    uid = str(request.from_user.id)

    if uid in users and users[uid]["paid"]:
        await bot.approve_chat_join_request(
            request.chat.id,
            request.from_user.id
        )

# ===== АДМИН ПАНЕЛЬ =====
@dp.message(Command("panel"))
async def panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("⚙️ Админ панель", reply_markup=admin_kb())

# ===== СТАТИСТИКА =====
@dp.callback_query(F.data == "a_stats")
async def stats(callback: CallbackQuery):
    total = len(users)
    paid = sum(1 for u in users.values() if u["paid"])

    await callback.message.edit_text(
        f"📊 Пользователей: {total}\n💸 Оплат: {paid}",
        reply_markup=admin_kb()
    )

# ===== СПИСОК =====
@dp.callback_query(F.data == "a_users")
async def list_users(callback: CallbackQuery):
    await callback.message.edit_text(
        f"👥 Всего пользователей: {len(users)}",
        reply_markup=admin_kb()
    )

# ===== ОПЛАТЫ =====
@dp.callback_query(F.data == "a_payments")
async def payments(callback: CallbackQuery):
    paid = [u for u in users if users[u]["paid"]]
    await callback.message.edit_text(
        f"💸 Оплатили: {len(paid)}",
        reply_markup=admin_kb()
    )

# ===== РАССЫЛКА =====
@dp.callback_query(F.data == "a_broadcast")
async def broadcast(callback: CallbackQuery):
    broadcast_mode.add(callback.from_user.id)
    await callback.message.edit_text("📢 Отправь текст или фото")

@dp.message()
async def send_broadcast(message: Message):
    if message.from_user.id not in broadcast_mode:
        return

    broadcast_mode.remove(message.from_user.id)

    sent = 0

    for uid in users:
        try:
            await bot.copy_message(uid, message.chat.id, message.message_id)
            sent += 1
            await asyncio.sleep(0.03)
        except:
            pass

    await message.answer(f"✅ Отправлено: {sent}")

# ===== БАН =====
@dp.callback_query(F.data == "a_ban")
async def ban_start(callback: CallbackQuery):
    await callback.message.edit_text("Введи ID пользователя для бана")

    @dp.message()
    async def ban_user(message: Message):
        try:
            banned.add(int(message.text))
            save_data()
            await message.answer("🚫 Забанен")
        except:
            pass

# ===== РАЗБАН =====
@dp.callback_query(F.data == "a_unban")
async def unban_start(callback: CallbackQuery):
    await callback.message.edit_text("Введи ID для разбана")

    @dp.message()
    async def unban_user(message: Message):
        try:
            banned.discard(int(message.text))
            save_data()
            await message.answer("✅ Разбанен")
        except:
            pass

# ===== ЗАПУСК =====
async def main():
    load_data()

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except Exception as e:
            print("Ошибка:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())