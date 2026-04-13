import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

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
        [InlineKeyboardButton(text="💳 Оплата", callback_data="pay")]
    ])

def paid_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")]
    ])

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🔥 Добро пожаловать\n\nВыберите действие:",
        reply_markup=main_kb()
    )

# ===== ОПЛАТА =====
@dp.callback_query(F.data == "pay")
async def pay(callback: CallbackQuery):
    await callback.message.edit_text(
        "💳 Оплата\n\n"
        "💰 120₽\n"
        "📌 2202208290305953\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=paid_kb()
    )

# ===== Я ОПЛАТИЛ =====
@dp.callback_query(F.data == "paid")
async def paid(callback: CallbackQuery):
    waiting_payment.add(callback.from_user.id)

    await callback.message.edit_text(
        "📸 Отправьте скрин оплаты"
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
        await msg.edit_text("❌ Ошибка отправки в группу")
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
    except Exception as e:
        status = "⚠️ Пользователь не подал заявку"
        print("APPROVE ERROR:", e)

    await bot.send_message(
        user_id,
        f"✅ Оплата подтверждена!\n\n"
        f"🔗 Вступить:\n{PRIVATE_LINK}\n\n"
        f"Подайте заявку"
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