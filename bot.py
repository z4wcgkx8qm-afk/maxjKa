from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
import asyncio
import os

BOT_TOKEN = "ВАШ_ТОКЕН_ТЕЛЕГРАМ_БОТА"
WEBAPP_URL = "https://ваш-проект.up.railway.app"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):
    btn = KeyboardButton(
        text="🔐 Войти в MAX",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    keyboard = ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)
    await message.answer("Нажмите кнопку для авторизации", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
