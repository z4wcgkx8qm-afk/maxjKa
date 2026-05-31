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
            background: #0a0a0a;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding-bottom: 80px;
            min-height: 100vh;
            background: radial-gradient(circle at 20% 30%, rgba(139,92,246,0.08), #0a0a0a 70%);
        }
        
        .card {
            background: #1a1a1a;
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.2);
            border: 1px solid #2a2a2a;
        }
        
        .header-card {
            background: #1a1a1a;
            border-radius: 0 0 24px 24px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.2);
            border-bottom: 1px solid #2a2a2a;
        }
        
        .header-title {
            font-size: 20px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 4px;
        }
        
        .header-sub {
            font-size: 13px;
            color: #8b5cf6;
            font-weight: 500;
        }
        
        .stats-row {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .stat-card {
            flex: 1;
            background: #1a1a1a;
            border-radius: 20px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.2);
            border: 1px solid #2a2a2a;
        }
        
        .stat-label {
            font-size: 11px;
            font-weight: 600;
            color: #888;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 800;
            color: #fff;
        }
        
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1a1a1a;
            border-radius: 28px 28px 0 0;
            padding: 10px 20px 25px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
            border-top: 1px solid #2a2a2a;
        }
        
        .nav-slider {
            display: flex;
            background: #2a2a2a;
            border-radius: 30px;
            padding: 4px;
        }
        
        .nav-item {
            flex: 1;
            text-align: center;
            padding: 10px 0;
            border-radius: 26px;
            font-size: 13px;
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
            padding: 0 16px;
        }
        
        .page.active {
            display: block;
        }
        
        .btn-primary {
            background: #8b5cf6;
            color: #fff;
            border: none;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            text-align: center;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .badge {
            background: #2a2a2a;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            color: #aaa;
        }
        
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 0;
            border-bottom: 1px solid #2a2a2a;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        .list-item-left {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .list-item-title {
            font-weight: 600;
            color: #fff;
            font-size: 15px;
        }
        
        .list-item-sub {
            font-size: 12px;
            color: #888;
        }
        
        .btn-small {
            background: #2a2a2a;
            border: none;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            color: #aaa;
            cursor: pointer;
        }
        
        .row-2cols {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .row-2cols > * {
            flex: 1;
        }
        
        .btn-outline {
            background: none;
            border: 1px solid #3a3a3a;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            color: #aaa;
            cursor: pointer;
            width: 100%;
            text-align: center;
        }
        
        .btn-danger {
            background: #2a1a1a;
            border: 1px solid #5a2a2a;
            color: #e77;
        }
        
        .personal-link-text {
            font-size: 12px;
            color: #8b5cf6;
            margin-top: 8px;
            word-break: break-all;
            text-align: center;
            padding: 12px;
            background: #0d0d0d;
            border-radius: 12px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .toast {
            position: fixed;
            bottom: 100px;
            left: 20px;
            right: 20px;
            background: #333;
            color: #fff;
            text-align: center;
            padding: 12px;
            border-radius: 30px;
            font-size: 14px;
            z-index: 1000;
            animation: fadeIn 0.3s ease-out;
        }
    </style>
</head>
<body>
    <div id="profilePage" class="page active">
        <div class="header-card">
            <div class="header-title">JANET ПАНЕЛЬ</div>
            <div class="header-sub">мини-приложение</div>
        </div>
        
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-label">АККАУНТЫ</div>
                <div class="stat-value" id="accountsCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">QR СЕГОДНЯ</div>
                <div class="stat-value" id="qrTodayCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">QR ЗА ВСЁ ВРЕМЯ</div>
                <div class="stat-value" id="qrTotalCount">0</div>
            </div>
        </div>
        
        <div class="card">
            <div style="text-align: center;">
                <span style="font-weight: 600; color: #fff;">Личный кабинет</span>
            </div>
            <div class="personal-link-text" id="personalLink">ожидайте общий домен</div>
            <button class="btn-primary" style="margin-top: 16px;" onclick="openLogin()">Перейти</button>
        </div>
    </div>
    
    <div id="accountsPage" class="page">
        <div class="header-card">
            <div class="header-title">JANET ПАНЕЛЬ</div>
            <div class="header-sub">мини-приложение</div>
        </div>
        
        <div class="card">
            <div class="section-title">
                <span>Мои Android-сессии</span>
                <span id="activeAccountBadge" class="badge">Активный: нет</span>
            </div>
            <div id="accountsList">
                <div style="text-align: center; padding: 20px; color: #888;">Аккаунтов пока нет</div>
            </div>
        </div>
        
        <div class="row-2cols">
            <button class="btn-outline" onclick="exportAccounts()">Выгрузить одним файлом</button>
            <button class="btn-outline btn-danger" onclick="deleteAllAccounts()">Удалить все аккаунты</button>
        </div>
    </div>
    
    <div class="bottom-nav">
        <div class="nav-slider" id="navSlider">
            <div class="nav-item active" data-page="profile">Ссылка</div>
            <div class="nav-item" data-page="accounts">Аккаунты</div>
        </div>
    </div>

    <script>
        const tg = Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        let appData = {
            accounts_count: 0,
            qr_today: 0,
            qr_total: 0,
            active_account: null,
            accounts_list: [],
            personal_link: "ожидайте общий домен",
            qr_chats: []
        };
        
        function showToast(msg) {
            const existing = document.querySelector('.toast');
            if (existing) existing.remove();
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = msg;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 2000);
        }
        
        function openLogin() {
            showToast('🚧 В разработке');
            tg.HapticFeedback.impactOccurred('medium');
        }
        
        function exportAccounts() {
            showToast('📁 Нет аккаунтов для выгрузки');
        }
        
        function deleteAllAccounts() {
            if (confirm('Удалить все аккаунты?')) {
                appData.accounts_list = [];
                appData.accounts_count = 0;
                appData.active_account = null;
                updateAccountsPage();
                updateStats();
                showToast('🗑️ Все аккаунты удалены');
                tg.HapticFeedback.impactOccurred('heavy');
            }
        }
        
        function selectAccount(phone) {
            appData.active_account = phone;
            updateAccountsPage();
            showToast(`✅ Активный: ${phone}`);
            tg.HapticFeedback.impactOccurred('light');
        }
        
        function updateProfilePage() {
            document.getElementById('accountsCount').innerText = appData.accounts_count;
            document.getElementById('qrTodayCount').innerText = appData.qr_today;
            document.getElementById('qrTotalCount').innerText = appData.qr_total;
            document.getElementById('personalLink').innerText = appData.personal_link;
        }
        
        function updateAccountsPage() {
            const container = document.getElementById('accountsList');
            const activeBadge = document.getElementById('activeAccountBadge');
            
            if (appData.accounts_list.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 20px; color: #888;">Аккаунтов пока нет</div>';
                activeBadge.innerText = 'Активный: нет';
                return;
            }
            
            activeBadge.innerText = appData.active_account ? `Активный: ${appData.active_account}` : 'Активный: нет';
            
            container.innerHTML = '';
            appData.accounts_list.forEach(acc => {
                const isActive = appData.active_account === acc.phone;
                container.innerHTML += `
                    <div class="list-item">
                        <div class="list-item-left">
                            <span class="list-item-title">${acc.name || acc.phone}</span>
                            <span class="list-item-sub">${acc.phone}</span>
                        </div>
                        <div class="list-item-right">
                            ${!isActive ? `<button class="btn-small" onclick="selectAccount('${acc.phone}')">Выбрать</button>` : '<span class="badge" style="background:#8b5cf6; color:#fff;">Активен</span>'}
                        </div>
                    </div>
                `;
            });
        }
        
        function updateStats() {
            document.getElementById('statsAccounts').innerText = appData.accounts_count;
            document.getElementById('statsToday').innerText = appData.qr_today;
            document.getElementById('statsTotal').innerText = appData.qr_total;
        }
        
        function updateAll() {
            updateProfilePage();
            updateAccountsPage();
            updateStats();
        }
        
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
        
        updateAll();
    </script>
</body>
</html>"""

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть JANET ПАНЕЛЬ", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
    ])
    await message.answer("🔐 Добро пожаловать в JANET ПАНЕЛЬ", reply_markup=keyboard)

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
    print(f"📱 JANET ПАНЕЛЬ: {WEBAPP_URL}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
