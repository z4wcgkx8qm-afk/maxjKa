import os
import asyncio
import json
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

CORRECT_PASSWORD = "601593"

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;touch-action:manipulation;}
        body{background:#fff;font-family:-apple-system,system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .container{width:100%;max-width:400px;padding:20px;}
        .title{text-align:center;font-size:32px;font-weight:bold;margin-bottom:40px;margin-top:60px;color:#000;}
        .subtitle{font-size:18px;color:#666;margin-bottom:30px;text-align:center;}
        .password-input{width:100%;padding:16px;font-size:24px;background:#f5f5f5;border:1px solid #ddd;border-radius:12px;color:#000;margin-bottom:30px;outline:none;text-align:center;letter-spacing:2px;}
        .password-input:focus{border-color:#8b5cf6;}
        .keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;}
        .key{background:#f5f5f5;border:none;border-radius:12px;padding:20px;font-size:24px;color:#000;cursor:pointer;transition:0.2s;touch-action:manipulation;}
        .key:active{background:#e0e0e0;}
        .key.backspace{background:#e0e0e0;font-size:18px;}
        .key.clear{background:#e0e0e0;}
        .status{margin-top:20px;text-align:center;font-size:14px;color:#ff4444;}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">Авторизация</div>
        <div class="subtitle">Введите пароль для входа в учетную запись Janet</div>
        <input type="password" id="password" class="password-input" readonly>
        <div class="keypad" id="keypad"></div>
        <div class="status" id="status"></div>
    </div>
    <script>
        const tg = Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        let password = '';
        const passwordInput = document.getElementById('password');
        const statusDiv = document.getElementById('status');
        
        const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '⌫', '0', 'C'];
        
        const keypad = document.getElementById('keypad');
        keys.forEach(key => {
            const btn = document.createElement('button');
            btn.className = 'key';
            if (key === '⌫') btn.classList.add('backspace');
            if (key === 'C') btn.classList.add('clear');
            btn.textContent = key;
            btn.onclick = () => handleKey(key);
            keypad.appendChild(btn);
        });
        
        function handleKey(key) {
            if (key === '⌫') {
                password = password.slice(0, -1);
                statusDiv.textContent = '';
            } else if (key === 'C') {
                password = '';
                statusDiv.textContent = '';
            } else {
                if (password.length < 6) {
                    password += key;
                }
            }
            passwordInput.value = '*'.repeat(password.length);
            
            if (password.length === 6) {
                login();
            }
        }
        
        function login() {
            tg.sendData(JSON.stringify({
                action: 'login',
                password: password
            }));
            tg.close();
        }
    </script>
</body>
</html>"""

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Войти в MAX", web_app=WebAppInfo(url=os.getenv("WEBAPP_URL")))]
    ])
    await message.answer("Нажмите кнопку для входа", reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    
    if data['action'] == 'login':
        password = data['password']
        
        if password == CORRECT_PASSWORD:
            await message.answer("✅ Пароль верный! Вход выполнен.")
        else:
            await message.answer("❌ Неверный пароль. Попробуйте снова.")

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
