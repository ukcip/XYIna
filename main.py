import asyncio
import random
import string
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

# ===== ТВОИ ДАННЫЕ =====
SCREEN_GROUP_ID = -1003421192077
THREAD_ID = 2

PRIVATE_CHAT_ID = -1003763565634
PRIVATE_LINK = "https://t.me/+O9tLSO8g5MsyYThi"

bot = Bot(token=TOKEN)
dp = Dispatcher()

waiting_payment = set()

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

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
        "Здесь вы можете приобрести доступ к привату💸\n\n"
        "👇 Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
        "👇 Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== КАРТА =====
@dp.callback_query(F.data == "card")
async def card(callback: CallbackQuery):
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
    await callback.message.edit_text(
        "💰 Оплата криптой\n\n"
        "http://t.me/send?start=IVWM9jtSGhiL\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=paid_kb()
    )

# ===== ЗВЕЗДЫ =====
@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ Оплата звёздами\n\n"
        "Отправьте админу @ukcip:\n"
        "• 50⭐ + 15⭐\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=paid_kb()
    )

# ===== ДОНАТ =====
@dp.callback_query(F.data == "donate")
async def donate(callback: CallbackQuery):
    await callback.message.edit_text(
        "💎 Донат\n\n"
        "💳 Карта: 2202208290305953\n"
        "💰 Крипта: http://t.me/send?start=IVjeLAEQlLzA",
        reply_markup=back_kb()
    )

# ===== Я ОПЛАТИЛ =====
@dp.callback_query(F.data == "paid")
async def paid(callback: CallbackQuery):
    waiting_payment.add(callback.from_user.id)

    await callback.message.edit_text(
        "📸 Отправьте скриншот оплаты"
    )

# ===== СКРИН =====
@dp.message(F.photo)
async def handle_photo(message: Message):
    if message.from_user.id not in waiting_payment:
        return

    waiting_payment.remove(message.from_user.id)

    msg = await message.answer("⏳ Обрабатываю оплату...")

    try:
        await bot.send_photo(
            chat_id=SCREEN_GROUP_ID,
            message_thread_id=THREAD_ID,
            photo=message.photo[-1].file_id,
            caption=(
                f"💸 Новая оплата\n\n"
                f"👤 ID: {message.from_user.id}\n"
                f"@{message.from_user.username}"
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Принять",
                        callback_data=f"accept_{message.from_user.id}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Отклонить",
                        callback_data=f"decline_{message.from_user.id}"
                    )
                ]
            ])
        )

        await asyncio.sleep(2)

        await msg.edit_text(
            "⏳ Ваша оплата на рассмотрении\n"
            "Ожидайте до 24 часов"
        )

    except Exception as e:
        await msg.edit_text("❌ Ошибка отправки")
        print("ERROR:", e)

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    try:
        await bot.approve_chat_join_request(
            chat_id=PRIVATE_CHAT_ID,
            user_id=user_id
        )
        status = "✅ Заявка одобрена"
    except:
        status = "⚠️ Нет заявки"

    await bot.send_message(
        user_id,
        f"✅ Оплата подтверждена!\n\n"
        f"🔗 {PRIVATE_LINK}"
    )

    await callback.message.edit_caption(f"✅ Принято\n\n{status}")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Оплата отклонена")
    await callback.message.edit_caption("❌ Отклонено")

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())