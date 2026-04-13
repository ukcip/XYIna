import asyncio
import random
import string

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

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ДАННЫЕ =====
users = set()
waiting_payment = set()
broadcast_mode = set()

# ===== АНИМАЦИЯ =====
async def loading(callback, text="⏳ Загрузка"):
    for i in range(3):
        try:
            await callback.message.edit_text(f"{text}{'.' * (i+1)}")
        except:
            pass
        await asyncio.sleep(0.4)

# ===== КОД =====
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

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
    users.add(message.from_user.id)

    await message.answer(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n\n"
        "Здесь вы можете приобрести доступ к привату💸\n\n"
        "👇 Выберите способ оплаты:",
        reply_markup=main_kb()
    )

# ===== НАЗАД =====
@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
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
    await loading(callback)

    await callback.message.edit_text(
        "💳 Оплата картой\n\n"
        "💰 120₽\n"
        "📌 2202208290305953\n\n"
        "После оплаты нажмите кнопку ниже 👇",
        reply_markup=paid_kb()
    )

# ===== КРИПТА =====
@dp.callback_query(F.data == "crypto")
async def crypto(callback: CallbackQuery):
    await loading(callback)

    await callback.message.edit_text(
        "💰 Оплата криптой\n\n"
        "http://t.me/send?start=IVWM9jtSGhiL\n\n"
        "После оплаты нажмите кнопку ниже 👇",
        reply_markup=paid_kb()
    )

# ===== ЗВЕЗДЫ =====
@dp.callback_query(F.data == "stars")
async def stars(callback: CallbackQuery):
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

    await message.answer("✅ Скрин отправлен на проверку")

# ===== ПРИНЯТЬ =====
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(
        user_id,
        f"✅ Ваша оплата рассмотрена\n\n"
        f"🔗 Ссылка на приват:\n{PRIVATE_LINK}\n\n"
        f"Подайте заявку и нажмите кнопку 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я отправил заявку", callback_data="joined")]
        ])
    )

    await callback.message.edit_caption("✅ Принято")

# ===== ОТКЛОНИТЬ =====
@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    await bot.send_message(user_id, "❌ Оплата не подтверждена")

    await callback.message.edit_caption("❌ Отклонено")

# ===== ПОДАЛ ЗАЯВКУ =====
@dp.callback_query(F.data == "joined")
async def joined(callback: CallbackQuery):
    await callback.message.edit_text("⏳ Ожидайте в течение 24 часов!")

# ===== РАССЫЛКА =====
@dp.message(Command("broadcast"))
async def broadcast_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode.add(message.from_user.id)
    await message.answer("📢 Отправь сообщение для рассылки")

@dp.message()
async def broadcast_send(message: Message):
    if message.from_user.id not in broadcast_mode:
        return

    broadcast_mode.remove(message.from_user.id)

    success = 0
    failed = 0

    for user_id in users:
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await message.answer(
        f"✅ Рассылка завершена\n\n"
        f"👤 Отправлено: {success}\n"
        f"❌ Ошибки: {failed}"
    )

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())