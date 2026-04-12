from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
import os
import asyncio

TOKEN = os.getenv("8657143749:AAEIPYqLeYTAWdJE26by9JPaELVHIY4fF6M")
GROUP_ID = -1003421192077
ADMIN_ID = 8250753514

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ------------------ FSM ------------------
class PaymentStates(StatesGroup):
    waiting_for_screenshot = State()

# ------------------ Клавиатуры ------------------
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплата картой"), KeyboardButton(text="Оплата криптой")],
        [KeyboardButton(text="Донат")]
    ],
    resize_keyboard=True
)

payment_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Я оплатил")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

# ------------------ Приветствие ------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🔥 Добро пожаловать в магазин от @ukcip📦\n"
        "Здесь вы можете приобрести доступ к привату💸\n"
        "Выберите способ оплаты:",
        reply_markup=main_kb
    )

# ------------------ Оплата ------------------
@dp.message(F.text.in_(["Оплата картой", "Оплата криптой"]))
async def start_payment(message: types.Message):
    await message.answer(
        "После оплаты нажмите кнопку 'Я оплатил'",
        reply_markup=payment_kb
    )

# ------------------ Я оплатил ------------------
@dp.message(F.text == "Я оплатил")
async def waiting_for_screenshot(message: types.Message, state: FSMContext):
    await message.answer("Пришлите скрин оплаты:")
    await state.set_state(PaymentStates.waiting_for_screenshot)

# ------------------ Получение скрина ------------------
@dp.message(PaymentStates.waiting_for_screenshot, F.photo)
async def screenshot_received(message: types.Message, state: FSMContext):
    await message.forward(GROUP_ID)

    await bot.send_message(
        GROUP_ID,
        f"Новая заявка от @{message.from_user.username or message.from_user.id}\n"
        f"ID: {message.from_user.id}"
    )

    await message.answer("Ваша оплата на рассмотрении, ожидайте до 24 часов")
    await state.clear()

# ------------------ Назад ------------------
@dp.message(F.text == "Назад")
async def go_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в меню", reply_markup=main_kb)

# ------------------ Донат ------------------
@dp.message(F.text == "Донат")
async def donate(message: types.Message):
    await message.answer(
        "💎 Поддержка проекта\n"
        "💰 Крипта: http://t.me/send?start=IVjeLAEQlLzA\n"
        "🪙 TON: UQDQo76coCyRrsJmrxiwakSU1765516jTjGfW7rHjHUqfHBu\n"
        "💳 Сбер: 2202208290305953"
    )

# ------------------ Админ ------------------
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_commands(message: types.Message):
    if message.text == "/ban":
        await message.answer("Бан выполнен")
    elif message.text == "/unban":
        await message.answer("Разбан выполнен")
    elif message.text == "/stats":
        await message.answer("Статистика")
    elif message.text == "/broadcast":
        await message.answer("Рассылка")

# ------------------ Запуск ------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())