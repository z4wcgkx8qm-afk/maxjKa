import os
import asyncio
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL").rstrip('/')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Данные пользователя (потом заменишь на БД)
USER_PASSWORD = "601593"
USER_DATA = {
    "accounts": 128,
    "today": 47,
    "total_qr": 2354
}

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            background: #fff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            min-height: 100vh;
        }
        
        /* Анимации */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .shake {
            animation: shake 0.3s ease-in-out;
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        /* Экран авторизации */
        .auth-screen {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .auth-container {
            width: 100%;
            max-width: 350px;
        }
        
        .logo {
            font-size: 48px;
            font-weight: 800;
            color: #000;
            text-align: center;
            margin-bottom: 60px;
            letter-spacing: 2px;
        }
        
        .subtitle {
            font-size: 16px;
            color: #666;
            text-align: center;
            margin-bottom: 40px;
        }
        
        .password-field {
            width: 100%;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            font-size: 32px;
            letter-spacing: 8px;
            font-weight: 600;
            color: #000;
            margin-bottom: 30px;
            font-family: monospace;
        }
        
        .keypad {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .key {
            background: #f5f5f5;
            border: none;
            border-radius: 16px;
            padding: 20px;
            font-size: 28px;
            font-weight: 500;
            color: #000;
            cursor: pointer;
            transition: all 0.15s ease;
            touch-action: manipulation;
        }
        
        .key:active {
            background: #e0e0e0;
            transform: scale(0.96);
        }
        
        .key.special {
            background: #e8e8e8;
            font-size: 20px;
        }
        
        .message {
            text-align: center;
            padding: 12px;
            border-radius: 12px;
            font-size: 14px;
            margin-top: 10px;
        }
        
        .message.error {
            background: #fee;
            color: #e33;
        }
        
        .message.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        /* Экран меню */
        .menu-screen {
            display: none;
            min-height: 100vh;
            background: #f8f9fa;
            padding: 20px;
            padding-bottom: 90px;
        }
        
        /* Верхняя карточка */
        .profile-card {
            background: #fff;
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        
        .profile-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .profile-label {
            font-size: 13px;
            font-weight: 600;
            color: #999;
            letter-spacing: 0.5px;
        }
        
        .refresh-btn {
            background: #f0f0f0;
            border: none;
            border-radius: 30px;
            padding: 8px 16px;
            font-size: 13px;
            color: #666;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        
        .refresh-btn:active {
            background: #e0e0e0;
            transform: scale(0.96);
        }
        
        .max-title {
            font-size: 44px;
            font-weight: 800;
            color: #000;
            text-align: center;
            letter-spacing: 2px;
        }
        
        /* Три карточки статистики */
        .stats-row {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            flex: 1;
            background: #fff;
            border-radius: 20px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        
        .stat-label {
            font-size: 11px;
            font-weight: 600;
            color: #999;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 800;
            color: #000;
        }
        
        /* Список */
        .list-card {
            background: #fff;
            border-radius: 20px;
            padding: 4px 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        .list-item-name {
            font-weight: 500;
            color: #000;
        }
        
        .list-item-value {
            color: #8b5cf6;
            font-weight: 500;
            font-size: 14px;
        }
        
        /* Навигация */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #fff;
            border-radius: 28px 28px 0 0;
            padding: 12px 20px 25px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
        }
        
        .nav-slider {
            display: flex;
            background: #f0f0f0;
            border-radius: 30px;
            padding: 4px;
        }
        
        .nav-item {
            flex: 1;
            text-align: center;
            padding: 10px 0;
            border-radius: 26px;
            font-size: 14px;
            font-weight: 500;
            color: #888;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .nav-item.active {
            background: #8b5cf6;
            color: #fff;
        }
        
        .page {
            display: none;
        }
        
        .page.active {
            display: block;
        }
    </style>
</head>
<body>
    <!-- Экран авторизации -->
    <div id="authScreen" class="auth-screen">
        <div class="auth-container">
            <div class="logo">MAX</div>
            <div class="subtitle">Введите пароль для входа<br>в учетную запись Janet</div>
            <div class="password-field" id="passwordDots">••••••</div>
            <div class="keypad" id="keypad"></div>
            <div id="message"></div>
        </div>
    </div>
    
    <!-- Экран меню -->
    <div id="menuScreen" class="menu-screen">
        <div id="profilePage" class="page active">
            <div class="profile-card">
                <div class="profile-header">
                    <span class="profile-label">ЛИЧНЫЙ КАБИНЕТ</span>
                    <button class="refresh-btn" onclick="refreshData()">🔄 Обновить</button>
                </div>
                <div class="max-title">MAX</div>
            </div>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-label">АККАУНТЫ</div>
                    <div class="stat-value" id="accountsValue">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">ЗА СЕГОДНЯ</div>
                    <div class="stat-value" id="todayValue">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">QR ВСЕГО</div>
                    <div class="stat-value" id="totalValue">0</div>
                </div>
            </div>
        </div>
        
        <div id="accountsPage" class="page">
            <div class="profile-card">
                <div class="profile-header">
                    <span class="profile-label">АККАУНТЫ MAX</span>
                </div>
            </div>
            <div class="list-card" id="accountsList"></div>
        </div>
        
        <div id="groupsPage" class="page">
            <div class="profile-card">
                <div class="profile-header">
                    <span class="profile-label">ГРУППЫ</span>
                </div>
            </div>
            <div class="list-card" id="groupsList"></div>
        </div>
        
        <div id="statsPage" class="page">
            <div class="profile-card">
                <div class="profile-header">
                    <span class="profile-label">СТАТИСТИКА</span>
                </div>
            </div>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-label">АККАУНТЫ</div>
                    <div class="stat-value" id="statsAccounts">0</div>
                </div>
            </div>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-label">QR СЕГОДНЯ</div>
                    <div class="stat-value" id="statsToday">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">QR ВСЕГО</div>
                    <div class="stat-value" id="statsTotal">0</div>
                </div>
            </div>
        </div>
        
        <div class="bottom-nav">
            <div class="nav-slider" id="navSlider">
                <div class="nav-item active" data-page="profile">Профиль</div>
                <div class="nav-item" data-page="accounts">Аккаунты</div>
                <div class="nav-item" data-page="groups">Группы</div>
                <div class="nav-item" data-page="stats">Статистика</div>
            </div>
        </div>
    </div>

    <script>
        const tg = Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        // Данные (потом будут с сервера)
        let appData = {
            accounts: 128,
            today: 47,
            total_qr: 2354,
            accounts_list: [
                {name: "Janet", phone: "+7 999 123-45-67"},
                {name: "John", phone: "+7 999 765-43-21"}
            ],
            groups_list: [
                {name: "MAX Community", members: 1243},
                {name: "Bot Developers", members: 567}
            ]
        };
        
        let currentPassword = '';
        const CORRECT_PASSWORD = "601593";
        
        // Отрисовка клавиатуры
        const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '⌫', '0', 'C'];
        const keypad = document.getElementById('keypad');
        
        keys.forEach(key => {
            const btn = document.createElement('button');
            btn.className = 'key';
            if (key === '⌫' || key === 'C') btn.classList.add('special');
            btn.textContent = key;
            btn.onclick = () => handleKey(key);
            keypad.appendChild(btn);
        });
        
        function handleKey(key) {
            const msgDiv = document.getElementById('message');
            msgDiv.innerHTML = '';
            
            if (key === '⌫') {
                currentPassword = currentPassword.slice(0, -1);
            } else if (key === 'C') {
                currentPassword = '';
            } else {
                if (currentPassword.length < 6) {
                    currentPassword += key;
                }
            }
            
            // Обновляем отображение
            const dots = document.getElementById('passwordDots');
            dots.textContent = '•'.repeat(currentPassword.length) + '••••••'.slice(currentPassword.length);
            
            // Проверяем при 6 цифрах
            if (currentPassword.length === 6) {
                if (currentPassword === CORRECT_PASSWORD) {
                    showSuccess();
                } else {
                    showError();
                }
            }
        }
        
        function showSuccess() {
            const msgDiv = document.getElementById('message');
            msgDiv.innerHTML = '<div class="message success fade-in">✅ Пароль верный!</div>';
            
            // Переключаем на меню через секунду
            setTimeout(() => {
                document.getElementById('authScreen').style.display = 'none';
                document.getElementById('menuScreen').style.display = 'block';
                updateAllData();
            }, 500);
        }
        
        function showError() {
            const msgDiv = document.getElementById('message');
            msgDiv.innerHTML = '<div class="message error fade-in shake">❌ Неверный пароль</div>';
            currentPassword = '';
            document.getElementById('passwordDots').textContent = '••••••';
            
            // Анимация поля
            const field = document.querySelector('.password-field');
            field.classList.add('shake');
            setTimeout(() => field.classList.remove('shake'), 300);
        }
        
        // Навигация
        document.querySelectorAll('.nav-item').forEach(item => {
            item.onclick = () => {
                const page = item.dataset.page;
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                
                document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
                document.getElementById(page + 'Page').classList.add('active');
                
                tg.HapticFeedback.impactOccurred('light');
            };
        });
        
        function updateAllData() {
            document.getElementById('accountsValue').innerText = appData.accounts;
            document.getElementById('todayValue').innerText = appData.today;
            document.getElementById('totalValue').innerText = appData.total_qr;
            document.getElementById('statsAccounts').innerText = appData.accounts;
            document.getElementById('statsToday').innerText = appData.today;
            document.getElementById('statsTotal').innerText = appData.total_qr;
            
            const accountsList = document.getElementById('accountsList');
            accountsList.innerHTML = '';
            appData.accounts_list.forEach(acc => {
                accountsList.innerHTML += `
                    <div class="list-item">
                        <span class="list-item-name">${acc.name}</span>
                        <span class="list-item-value">${acc.phone}</span>
                    </div>
                `;
            });
            
            const groupsList = document.getElementById('groupsList');
            groupsList.innerHTML = '';
            appData.groups_list.forEach(group => {
                groupsList.innerHTML += `
                    <div class="list-item">
                        <span class="list-item-name">${group.name}</span>
                        <span class="list-item-value">${group.members} участников</span>
                    </div>
                `;
            });
        }
        
        function refreshData() {
            tg.HapticFeedback.impactOccurred('medium');
            // TODO: запрос к серверу за свежими данными
            updateAllData();
        }
    </script>
</body>
</html>"""

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть MAX", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
    ])
    await message.answer("🔐 Добро пожаловать в MAX", reply_markup=keyboard)

async def handle_main(request):
    return web.Response(text=HTML, content_type="text/html")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_main)
    app.router.add_post("/webhook", SimpleRequestHandler(dispatcher=dp, bot=bot).handle)
    setup_application(app, dp, bot=bot)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    
    await bot.set_webhook(f"{WEBAPP_URL}/webhook")
    
    print(f"✅ Бот запущен")
    print(f"📱 Mini App: {WEBAPP_URL}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
