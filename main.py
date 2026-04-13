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

# ===== СОХРАНЕНИЕ =====
def save():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": list(users),
            "banned": list(banned)
        }, f)

def load():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    users.update(data.get("users", []))
    banned.update(data.get("banned", []))

# ===== КНОПКИ =====
def panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="p_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="p_broadcast")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="p_users")],
        [InlineKeyboardButton(text="🚫 Бан", callback_data="p_ban")],
        [InlineKeyboardButton(text="✅ Разбан", callback_data="p_unban")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id in banned:
        return

    users.add(message.from_user.id)
    save()

    await message.answer("🔥 Добро пожаловать")

# ===== ПАНЕЛЬ =====
@dp.message(Command("panel"))
async def panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("⚙️ PRO Панель", reply_markup=panel_kb())

# ===== СТАТА =====
@dp.callback_query(F.data == "p_stats")
async def stats(callback: CallbackQuery):
    await callback.message.edit_text(
        f"📊 Пользователей: {len(users)}\n🚫 Забанено: {len(banned)}",
        reply_markup=panel_kb()
    )

# ===== ПОЛЬЗОВАТЕЛИ =====
@dp.callback_query(F.data == "p_users")
async def users_list(callback: CallbackQuery):
    await callback.message.edit_text(
        f"👥 Всего пользователей: {len(users)}",
        reply_markup=panel_kb()
    )

# ===== РАССЫЛКА =====
@dp.callback_query(F.data == "p_broadcast")
async def broadcast(callback: CallbackQuery):
    broadcast_mode.add(callback.from_user.id)

    await callback.message.edit_text("📢 Отправь сообщение")

# ===== ОТПРАВКА =====
@dp.message()
async def send_broadcast(message: Message):
    if message.from_user.id not in broadcast_mode:
        return

    broadcast_mode.remove(message.from_user.id)

    sent = 0

    for user in users:
        try:
            await bot.copy_message(user, message.chat.id, message.message_id)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass

    await message.answer(f"✅ Отправлено: {sent}")

# ===== БАН =====
@dp.callback_query(F.data == "p_ban")
async def ban_start(callback: CallbackQuery):
    await callback.message.edit_text("🚫 Введи ID пользователя")

    dp.message.register(ban_user)

async def ban_user(message: Message):
    try:
        user_id = int(message.text)
        banned.add(user_id)
        save()

        await message.answer("✅ Пользователь забанен")
    except:
        await message.answer("❌ Ошибка")

# ===== РАЗБАН =====
@dp.callback_query(F.data == "p_unban")
async def unban_start(callback: CallbackQuery):
    await callback.message.edit_text("✅ Введи ID пользователя")

    dp.message.register(unban_user)

async def unban_user(message: Message):
    try:
        user_id = int(message.text)
        banned.discard(user_id)
        save()

        await message.answer("✅ Разбанен")
    except:
        await message.answer("❌ Ошибка")

# ===== АВТО-ПРИНЯТИЕ =====
@dp.chat_join_request()
async def auto_accept(request: ChatJoinRequest):
    try:
        await bot.approve_chat_join_request(
            chat_id=request.chat.id,
            user_id=request.from_user.id
        )
    except:
        pass

# ===== АВТОРЕСТАРТ =====
async def main():
    load()

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except Exception as e:
            print("Ошибка:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())