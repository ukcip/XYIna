import asyncio
import random
import string

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ReplyKeyboardRemove
)
from aiogram.filters import Command

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

bot = Bot(token=TOKEN)
dp = Dispatcher()

codes = {}

# ===== ГЕНЕРАЦИЯ КОДА =====
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ===== АНИМАЦИЯ =====
async def loading(callback, text="⏳ Загрузка"):
    for i in range(3):
        dots = "." * (i + 1)
        try:
            await callback.message.edit_text(f"{text}{dots}")
        except:
            pass
        await asyncio.sleep(0.5)

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

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    # 💥 УДАЛЯЕМ старые кнопки
    await message.answer(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n"
        "Здесь вы можете приобрести доступ к привату💸",
        reply_markup=ReplyKeyboardRemove()
    )

    # 👉 создаем одно основное сообщение
    await message.answer(
        "Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await loading(callback)

    await callback.message.edit_text(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n"
        "Здесь вы можете приобрести доступ к привату💸\n\n"
        "Выберите способ оплаты:",
        reply_markup=main_kb()
    )
    await callback.answer()

# ===== КАРТА =====
@dp.callback_query(F.data == "card")
async def card(callback: CallbackQuery):
    await loading(callback, "⏳ Подготовка оплаты")

    code = generate_code()
    codes[callback.from_user.id] = code

    await callback.message.edit_text(
        f"💳 Оплата картой\n\n"
        f"💰 120₽\n"
        f"📌 2202208290305953\n"
        f"Сбербанк | Даниил С.\n\n"
        f"❗ УКАЖИТЕ КОД:\n👉 {code}",
        reply_markup=back_kb()
    )
    await callback.answer()

# ===== КРИПТА =====
@dp.callback_query(F.data == "crypto")
async def crypto(callback: CallbackQuery):
    await loading(callback, "⏳ Генерация ссылки")

    code = generate_code()
    codes[callback.from_user.id] = code

    await callback.message.edit_text(
        f"💰 Оплата криптой:\n"
        f"http://t.me/send?start=IVWM9jtSGhiL\n\n"
        f"❗ УКАЖИТЕ КОД:\n👉 {code}",
        reply_markup=back_kb()
    )
    await callback.answer()

# ===== ЗВЕЗДЫ =====
@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
    await loading(callback, "⏳ Загрузка оплаты")

    await callback.message.edit_text(
        "⭐ Оплата звёздами\n\n"
        "📌 Отправьте админу @ukcip:\n"
        "• 50 ⭐\n"
        "• затем 15 ⭐\n\n"
        "⏳ Выдача в течение 24 часов",
        reply_markup=back_kb()
    )
    await callback.answer()

# ===== ДОНАТ =====
@dp.callback_query(F.data == "donate")
async def donate(callback: CallbackQuery):
    await loading(callback)

    await callback.message.edit_text(
        "💎 Поддержка проекта\n\n"
        "💰 Крипта: http://t.me/send?start=IVjeLAEQlLzA\n"
        "🪙 TON: UQDQo76coCyRrsJmrxiwakSU1765516jTjGfW7rHjHUqfHBu\n"
        "💳 Сбербанк: 2202208290305953",
        reply_markup=back_kb()
    )
    await callback.answer()

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())