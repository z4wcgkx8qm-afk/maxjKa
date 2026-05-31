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

# Данные для меню (заглушка, потом из БД)
user_data = {
    "accounts": 128,
    "today": 47,
    "total_qr": 2354
}

HTML_AUTH = """<!DOCTYPE html>
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
        }
    </script>
</body>
</html>"""

HTML_MENU = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;touch-action:manipulation;}
        body{background:#f0f0f0;font-family:-apple-system,system-ui,sans-serif;padding:20px;}
        
        /* Верхняя рамка */
        .top-card{background:#fff;border-radius:20px;padding:20px;margin-bottom:20px;box-shadow:0 2px 10px rgba(0,0,0,0.05);}
        .top-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
        .top-header-left{font-size:14px;font-weight:600;color:#888;letter-spacing:0.5px;}
        .refresh-btn{background:#f5f5f5;border:none;border-radius:30px;padding:8px 16px;font-size:13px;color:#666;cursor:pointer;}
        .max-logo{font-size:48px;font-weight:800;color:#000;text-align:center;letter-spacing:2px;}
        
        /* Три карточки в ряд */
        .stats-row{display:flex;gap:12px;margin-bottom:20px;}
        .stat-card{flex:1;background:#fff;border-radius:20px;padding:16px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.05);}
        .stat-label{font-size:11px;font-weight:600;color:#888;letter-spacing:0.5px;margin-bottom:12px;}
        .stat-value{font-size:28px;font-weight:800;color:#000;}
        
        /* Навигация внизу */
        .bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#fff;border-radius:25px 25px 0 0;padding:12px 20px 25px;box-shadow:0 -2px 20px rgba(0,0,0,0.05);}
        .nav-slider{display:flex;background:#f0f0f0;border-radius:30px;padding:4px;margin-bottom:10px;}
        .slider-item{flex:1;text-align:center;padding:8px 0;border-radius:25px;font-size:14px;font-weight:500;color:#888;cursor:pointer;transition:0.2s;}
        .slider-item.active{background:#8b5cf6;color:#fff;}
        .nav-items{display:flex;justify-content:space-around;}
        .nav-text{font-size:12px;color:#888;margin-top:8px;text-align:center;}
        
        .content-page{display:none;}
        .content-page.active{display:block;margin-bottom:100px;}
        
        .list-item{background:#fff;border-radius:15px;padding:15px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;}
        .list-item-name{font-weight:600;color:#000;}
        .list-item-value{color:#8b5cf6;font-weight:600;}
    </style>
</head>
<body>
    <div id="profilePage" class="content-page active">
        <div class="top-card">
            <div class="top-header">
                <span class="top-header-left">ЛИЧНЫЙ КАБИНЕТ</span>
                <button class="refresh-btn" onclick="refresh()">🔄 Обновить</button>
            </div>
            <div class="max-logo">MAX</div>
        </div>
        
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-label">АККАУНТЫ</div>
                <div class="stat-value" id="accountsValue">128</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">ЗА СЕГОДНЯ</div>
                <div class="stat-value" id="todayValue">47</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">QR ЗА ВСЕ ВРЕМЯ</div>
                <div class="stat-value" id="totalQrValue">2354</div>
            </div>
        </div>
    </div>
    
    <div id="accountsPage" class="content-page">
        <div class="top-card">
            <div class="top-header">
                <span class="top-header-left">АККАУНТЫ MAX</span>
            </div>
        </div>
        <div id="accountsList"></div>
    </div>
    
    <div id="groupsPage" class="content-page">
        <div class="top-card">
            <div class="top-header">
                <span class="top-header-left">ГРУППЫ</span>
            </div>
        </div>
        <div id="groupsList"></div>
    </div>
    
    <div id="statsPage" class="content-page">
        <div class="top-card">
            <div class="top-header">
                <span class="top-header-left">СТАТИСТИКА</span>
            </div>
        </div>
        <div class="stat-card" style="margin-bottom:10px;">
            <div class="stat-label">ВСЕГО АККАУНТОВ</div>
            <div class="stat-value" id="statsAccounts">128</div>
        </div>
        <div class="stat-card" style="margin-bottom:10px;">
            <div class="stat-label">QR СЕГОДНЯ</div>
            <div class="stat-value" id="statsToday">47</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">QR ВСЕГО</div>
            <div class="stat-value" id="statsTotal">2354</div>
        </div>
    </div>
    
    <div class="bottom-nav">
        <div class="nav-slider" id="navSlider">
            <div class="slider-item active" data-page="profile">Профиль</div>
            <div class="slider-item" data-page="accounts">Аккаунты</div>
            <div class="slider-item" data-page="groups">Группы</div>
            <div class="slider-item" data-page="stats">Статистика</div>
        </div>
    </div>

    <script>
        const tg = Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        let currentPage = 'profile';
        
        function switchPage(page) {
            document.querySelectorAll('.content-page').forEach(p => p.classList.remove('active'));
            document.getElementById(page + 'Page').classList.add('active');
            
            document.querySelectorAll('.slider-item').forEach(item => {
                item.classList.remove('active');
                if(item.dataset.page === page) item.classList.add('active');
            });
            
            currentPage = page;
        }
        
        document.querySelectorAll('.slider-item').forEach(item => {
            item.onclick = () => switchPage(item.dataset.page);
        });
        
        function refresh() {
            tg.sendData(JSON.stringify({action: 'refresh'}));
        }
        
        function updateData(data) {
            document.getElementById('accountsValue').innerText = data.accounts;
            document.getElementById('todayValue').innerText = data.today;
            document.getElementById('totalQrValue').innerText = data.total_qr;
            document.getElementById('statsAccounts').innerText = data.accounts;
            document.getElementById('statsToday').innerText = data.today;
            document.getElementById('statsTotal').innerText = data.total_qr;
            
            const accountsList = document.getElementById('accountsList');
            accountsList.innerHTML = '';
            data.accounts_list?.forEach(acc => {
                accountsList.innerHTML += `<div class="list-item"><span class="list-item-name">${acc.name}</span><span class="list-item-value">${acc.phone}</span></div>`;
            });
            
            const groupsList = document.getElementById('groupsList');
            groupsList.innerHTML = '';
            data.groups_list?.forEach(group => {
                groupsList.innerHTML += `<div class="list-item"><span class="list-item-name">${group.name}</span><span class="list-item-value">${group.members} участников</span></div>`;
            });
        }
        
        // Заглушка данных
        updateData({
            accounts: 128,
            today: 47,
            total_qr: 2354,
            accounts_list: [{name: "Janet", phone: "+7 999 123-45-67"}, {name: "John", phone: "+7 999 765-43-21"}],
            groups_list: [{name: "MAX Community", members: 1243}, {name: "Bot Developers", members: 567}]
        });
    </script>
</body>
</html>"""

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Войти в MAX", web_app=WebAppInfo(url=os.getenv("WEBAPP_URL") + "/auth"))]
    ])
    await message.answer("Нажмите кнопку для входа", reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    
    if data.get('action') == 'login':
        password = data['password']
        if password == CORRECT_PASSWORD:
            await message.answer("✅ Пароль верный!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Открыть меню", web_app=WebAppInfo(url=os.getenv("WEBAPP_URL") + "/menu"))]
            ]))
        else:
            await message.answer("❌ Неверный пароль. Попробуйте снова.")
    
    elif data.get('action') == 'refresh':
        # TODO: загрузить свежие данные из БД
        await message.answer(json.dumps(user_data))

async def handle_auth(request):
    return web.Response(text=HTML_AUTH, content_type="text/html")

async def handle_menu(request):
    return web.Response(text=HTML_MENU, content_type="text/html")

async def main():
    app = web.Application()
    app.router.add_get("/auth", handle_auth)
    app.router.add_get("/menu", handle_menu)
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
