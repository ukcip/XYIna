import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ContentType

TOKEN = "8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ID
ADMIN_ID = 8250753514
GROUP_ID = -1003421192077

# Кнопки
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплата")],
        [KeyboardButton(text="✅ Я оплатил")]
    ],
    resize_keyboard=True
)

# Старт
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=kb
    )

# Оплата
@dp.message(F.text == "💳 Оплата")
async def pay(message: Message):
    await message.answer(
        "💸 Оплата криптой:\n"
        "https://t.me/send?start=IVWM9jtSGhiL\n\n"
        "После оплаты нажмите '✅ Я оплатил'"
    )

# Нажал "Я оплатил"
@dp.message(F.text == "✅ Я оплатил")
async def paid(message: Message):
    await message.answer("📸 Пришлите скриншот оплаты")

# Приём СКРИНА (ФОТО)
@dp.message(F.photo)
async def screenshot(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    caption = f"💸 Новая оплата!\nID: {user_id}\n@{username}"

    # Отправка в группу
    await bot.send_photo(
        chat_id=GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=caption
    )

    await message.answer("⏳ Ваша оплата на рассмотрении, ожидайте 24 часа")

# Команда админа (ответ на сообщение)
@dp.message(Command("accept"))
async def accept(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        await message.answer("Ответь на сообщение со скрином")
        return

    text = message.reply_to_message.caption

    if not text:
        return

    # достаём ID
    user_id = int(text.split("ID: ")[1].split("\n")[0])

    await bot.send_message(
        user_id,
        "✅ Ваша оплата рассмотрена!\n\n"
        "Ссылка на приват:\n"
        "https://t.me/+O9tLSO8g5MsyYThi\n\n"
        "Нажмите кнопку ниже"
    )

    kb2 = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📩 Я отправил заявку")]],
        resize_keyboard=True
    )

    await bot.send_message(user_id, "После подачи нажмите:", reply_markup=kb2)

# Кнопка "Я отправил заявку"
@dp.message(F.text == "📩 Я отправил заявку")
async def done(message: Message):
    await message.answer("⏳ Ожидайте подтверждения в течение 24 часов")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())