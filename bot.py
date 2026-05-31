import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:#000;font-family:-apple-system,system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .container{width:100%;max-width:400px;padding:20px;}
        .header{position:fixed;top:20px;left:20px;}
        .max-logo{color:#fff;font-size:24px;font-weight:bold;}
        .content{margin-top:80px;}
        .phone-input{width:100%;padding:16px;font-size:18px;background:#1a1a1a;border:1px solid #333;border-radius:12px;color:#fff;margin-bottom:20px;outline:none;}
        .phone-input:focus{border-color:#8b5cf6;}
        .purple-button{width:100%;padding:16px;font-size:18px;font-weight:600;background:#8b5cf6;color:#fff;border:none;border-radius:30px;cursor:pointer;}
        .purple-button:active{opacity:0.8;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><div class="max-logo">MAX</div></div>
        <div class="content">
            <input type="tel" id="phone" class="phone-input" placeholder="+7 123 456-78-90">
            <button class="purple-button" onclick="sendPhone()">Получить код</button>
        </div>
    </div>
    <script>
        const tg = Telegram.WebApp;
        tg.expand();
        tg.ready();
        function sendPhone(){
            const phone = document.getElementById('phone').value;
            tg.sendData(JSON.stringify({phone: phone}));
            tg.close();
        }
    </script>
</body>
</html>"""

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Авторизация MAX", web_app=WebAppInfo(url=os.getenv("WEBAPP_URL")))]
    ])
    await message.answer("Нажмите кнопку для авторизации в MAX", reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    # Здесь будет обработка номера телефона через PyMax
    await message.answer(f"Получен номер: {message.web_app_data.data}")

async def handle_webapp(request):
    return web.Response(text=HTML, content_type="text/html")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_webapp)
    app.router.add_post("/webhook", SimpleRequestHandler(dispatcher=dp, bot=bot).handle)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))
    print(f"Бот запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
