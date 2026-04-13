import asyncio
import random
import string

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

GROUP_ID = -1003421192077
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== АНТИ-ФЛУД =====
async def safe_send(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        return await func(*args, **kwargs)

# ===== АВТО-УДАЛЕНИЕ =====
async def auto_delete(msg, delay=30):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ===== КОДЫ =====
codes = {}

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ===== ГЛАВНОЕ МЕНЮ =====
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

# ===== НАЗАД =====
def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    msg = await safe_send(
        message.answer,
        "🔥 Добро пожаловать в магазин от @ukcip📦\n"
        "Здесь вы можете приобрести доступ к привату💸\n\n"
        "Выберите способ оплаты:",
        reply_markup=main_kb()
    )
    asyncio.create_task(auto_delete(msg))

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await start(callback.message)
    await callback.answer()

# ===== КАРТА =====
@dp.callback_query(F.data == "card")
async def card(callback: CallbackQuery):
    code = generate_code()
    codes[callback.from_user.id] = code

    msg = await safe_send(
        callback.message.answer,
        f"💳 Оплата картой\n\n"
        f"💰 120₽\n"
        f"📌 2202208290305953\n"
        f"Сбербанк | Даниил С.\n\n"
        f"❗ УКАЖИТЕ КОД:\n👉 {code}",
        reply_markup=back_kb()
    )

    asyncio.create_task(auto_delete(msg))
    await callback.answer()

# ===== КРИПТА =====
@dp.callback_query(F.data == "crypto")
async def crypto(callback: CallbackQuery):
    code = generate_code()
    codes[callback.from_user.id] = code

    msg = await safe_send(
        callback.message.answer,
        f"💰 Оплата криптой:\n"
        f"http://t.me/send?start=IVWM9jtSGhiL\n\n"
        f"❗ УКАЖИТЕ КОД:\n👉 {code}",
        reply_markup=back_kb()
    )

    asyncio.create_task(auto_delete(msg))
    await callback.answer()

# ===== ЗВЕЗДЫ =====
@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
    msg = await safe_send(
        callback.message.answer,
        "⭐ Оплата звёздами\n\n"
        "📌 Отправьте админу @ukcip:\n"
        "• 50 ⭐\n"
        "• затем 15 ⭐\n\n"
        "⏳ Выдача в течение 24 часов",
        reply_markup=back_kb()
    )

    asyncio.create_task(auto_delete(msg))
    await callback.answer()

# ===== ДОНАТ =====
@dp.callback_query(F.data == "donate")
async def donate(callback: CallbackQuery):
    msg = await safe_send(
        callback.message.answer,
        "💎 Поддержать проект\n\n"
        "💰 Крипта: http://t.me/send?start=IVjeLAEQlLzA\n"
        "🪙 TON: UQDQo76coCyRrsJmrxiwakSU1765516jTjGfW7rHjHUqfHBu\n"
        "💳 Сбербанк: 2202208290305953 Даниил С.",
        reply_markup=back_kb()
    )

    asyncio.create_task(auto_delete(msg))
    await callback.answer()

# ===== СКРИН =====
@dp.message(F.photo)
async def screenshot(message: Message):
    user = message.from_user
    code = codes.get(user.id)

    text = (message.caption or "").upper()

    if code and code in text:
        status = "✅ КОД НАЙДЕН"
    else:
        status = "❌ КОД НЕ НАЙДЕН (ВОЗМОЖЕН ФЕЙК)"

    caption = (
        f"{status}\n\n"
        f"👤 @{user.username}\n"
        f"🆔 {user.id}\n"
        f"🔑 Код: {code}"
    )

    kb_inline = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{user.id}")
        ]
    ])

    await safe_send(
        bot.send_photo,
        GROUP_ID,
        message.photo[-1].file_id,
        caption=caption,
        reply_markup=kb_inline
    )

    msg = await safe_send(message.answer, "⏳ Оплата отправлена на проверку")
    asyncio.create_task(auto_delete(msg))

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await safe_send(
        bot.send_message,
        user_id,
        f"✅ Оплата подтверждена!\n\n🔗 {PRIVATE_LINK}"
    )

    await callback.answer("Принято")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await safe_send(
        bot.send_message,
        user_id,
        "❌ Оплата отклонена"
    )

    await callback.answer("Отклонено")

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())