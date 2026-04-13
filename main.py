import asyncio
import random
import string

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

GROUP_ID = -1003421192077
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище кодов (user_id: code)
codes = {}

# --- генерация кода ---
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- клавиатура ---
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплата картой"), KeyboardButton(text="💰 Оплата криптой")],
        [KeyboardButton(text="✅ Я оплатил")]
    ],
    resize_keyboard=True
)

# --- старт ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Выберите способ оплаты:", reply_markup=kb)

# --- оплата ---
@dp.message(F.text.in_(["💳 Оплата картой", "💰 Оплата криптой"]))
async def payment(message: Message):
    code = generate_code()
    codes[message.from_user.id] = code

    await message.answer(
        f"💸 Оплатите и ОБЯЗАТЕЛЬНО укажите код в комментарии:\n\n"
        f"👉 {code}\n\n"
        f"После оплаты нажмите 'Я оплатил'"
    )

# --- я оплатил ---
@dp.message(F.text == "✅ Я оплатил")
async def paid(message: Message):
    await message.answer("📸 Пришлите скрин оплаты С ВИДНЫМ КОДОМ")

# --- обработка скрина ---
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

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_{user.id}")
        ]
    ])

    await bot.send_photo(
        GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        reply_markup=kb
    )

    await message.answer("⏳ Ваша оплата отправлена на проверку")

# --- принять ---
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(
        user_id,
        f"✅ Оплата подтверждена\n\n🔗 {PRIVATE_LINK}"
    )

    await callback.answer("Принято")

# --- отклонить ---
@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Оплата отклонена")
    await callback.answer("Отклонено")

# --- запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())