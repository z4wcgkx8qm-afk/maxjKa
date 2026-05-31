import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINIAPP_URL = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def handle_miniapp(request):
    return web.FileResponse('miniapp.html')

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("👋 Нажми кнопку чтобы открыть MAX", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Открыть MAX", web_app=WebAppInfo(url=MINIAPP_URL))]
    ]))

@dp.message(F.web_app_data)
async def web_app(msg: Message):
    await msg.answer(f"✅ Данные получены")

async def main():
    app = web.Application()
    app.router.add_get('/', handle_miniapp)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info(f"Mini App: {MINIAPP_URL}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
