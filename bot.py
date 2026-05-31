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

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:#000;font-family:-apple-system,system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .container{width:100%;max-width:400px;padding:20px;}
        .title{text-align:center;font-size:32px;font-weight:bold;margin-bottom:40px;margin-top:60px;}
        .subtitle{font-size:18px;color:#aaa;margin-bottom:30px;text-align:center;}
        .password-input{width:100%;padding:16px;font-size:24px;background:#1a1a1a;border:1px solid #333;border-radius:12px;color:#fff;margin-bottom:30px;outline:none;text-align:center;letter-spacing:2px;}
        .password-input:focus{border-color:#8b5cf6;}
        .keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;}
        .key{background:#1a1a1a;border:none;border-radius:12px;padding:20px;font-size:24px;color:#fff;cursor:pointer;transition:0.2s;}
        .key:active{background:#333;}
        .key.backspace{background:#333;font-size:18px;}
        .key.clear{background:#333;}
        .status{margin-top:20px;text-align:center;font-size:14px;color:#8b5cf6;}
    </style>
</head>
<body>
    <div class="container">
        <div class="title" id="title">Авторизация</div>
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
        
        const initData = tg.initDataUnsafe;
        const userId = initData.user?.id;
        
        async function checkRegistration() {
            tg.sendData(JSON.stringify({action: 'check', user_id: userId}));
        }
        
        checkRegistration();
        
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
            } else if (key === 'C') {
                password = '';
            } else {
                if (password.length < 6) {
                    password += key;
                }
            }
            passwordInput.value = '*'.repeat(password.length);
            
            // Автоматический вход при вводе 4-6 цифр
            if (password.length >= 4 && password.length <= 6) {
                login();
            }
        }
        
        function login() {
            tg.sendData(JSON.stringify({
                action: 'login',
                user_id: userId,
                password: password
            }));
            tg.close();
        }
        
        window.handleTelegram = function(data) {
            if (data.registered) {
                document.getElementById('title').textContent = 'Авторизация';
            } else {
                document.getElementById('title').textContent = 'Регистрация';
            }
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
    
    if data['action'] == 'check':
        user_id = data['user_id']
        registered = False  # TODO: подключить PostgreSQL
        await message.answer(json.dumps({'registered': registered}))
    
    elif data['action'] == 'login':
        user_id = data['user_id']
        password = data['password']
        # TODO: проверка/создание пароля в PostgreSQL
        await message.answer(f"✅ Вход выполнен для user {user_id}")

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
