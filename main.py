import asyncio
import random
import string

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

GROUP_ID = -1003421192077
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== АНТИ-ФЛУД ФУНКЦИЯ =====
async def safe_send(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        return await func(*args, **kwargs)

# ===== ХРАНЕНИЕ КОДОВ =====
codes = {}

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ===== КНОПКИ =====
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплата картой"), KeyboardButton(text="💰 Оплата криптой")],
        [KeyboardButton(text="✅ Я оплатил")]
    ],
    resize_keyboard=True
)

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    await safe_send(message.answer, "Выберите способ оплаты:", reply_markup=kb)

# ===== ОПЛАТА =====
@dp.message(F.text.in_(["💳 Оплата картой", "💰 Оплата криптой"]))
async def payment(message: Message):
    code = generate_code()
    codes[message.from_user.id] = code

    await safe_send(
        message.answer,
        f"💸 Оплатите и укажите код в комментарии:\n\n👉 {code}\n\nПосле оплаты нажмите 'Я оплатил'"
    )

# ===== Я ОПЛАТИЛ =====
@dp.message(F.text == "✅ Я оплатил")
async def paid(message: Message):
    await safe_send(message.answer, "📸 Пришлите скрин оплаты С ВИДНЫМ КОДОМ")

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

    await safe_send(message.answer, "⏳ Ваша оплата отправлена на проверку")

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