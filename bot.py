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
            background: #f8f9fa;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding-bottom: 80px;
        }
        
        .purple-bg {
            background: #8b5cf6;
        }
        
        .purple-text {
            color: #8b5cf6;
        }
        
        .card {
            background: #fff;
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        
        .header-card {
            background: #fff;
            border-radius: 0 0 24px 24px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        
        .header-title {
            font-size: 20px;
            font-weight: 700;
            color: #000;
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
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 800;
            color: #000;
        }
        
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 0;
            border-bottom: 1px solid #f0f0f0;
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
            color: #000;
            font-size: 15px;
        }
        
        .list-item-sub {
            font-size: 12px;
            color: #999;
        }
        
        .list-item-right {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .badge {
            background: #f0f0f0;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            color: #666;
        }
        
        .btn-link {
            background: none;
            border: none;
            color: #8b5cf6;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
        }
        
        .btn-small {
            background: #f0f0f0;
            border: none;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            color: #666;
            cursor: pointer;
        }
        
        .btn-danger {
            background: #fee;
            color: #e33;
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
        
        .btn-outline {
            background: none;
            border: 1px solid #e0e0e0;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            color: #666;
            cursor: pointer;
            width: 100%;
            text-align: center;
        }
        
        .row-2cols {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .row-2cols > * {
            flex: 1;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #000;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .qr-chat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .qr-code {
            font-family: monospace;
            font-size: 13px;
            background: #f5f5f5;
            padding: 4px 8px;
            border-radius: 8px;
            color: #333;
        }
        
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #fff;
            border-radius: 28px 28px 0 0;
            padding: 10px 20px 25px;
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
        
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 15px; color: #666;">Лучший кабинет</span>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 24px; font-weight: 800;">max</span>
                    <span style="font-size: 20px;">👤</span>
                </div>
            </div>
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
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <span style="font-weight: 600;">Личный кабинет</span>
                <button class="btn-small" onclick="copyLink()">Копировать</button>
            </div>
            <div style="font-size: 12px; color: #8b5cf6; margin-top: 8px; word-break: break-all;" id="personalLink">https://maxinfo.lol/?t=ODcwNjcxMjIyOQ.SbWnR6z0FVzl6YfVKduCf9c1QcZaJbwZ</div>
            <button class="btn-primary" style="margin-top: 16px;" onclick="openLogin()">Открыть вход</button>
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
                <div style="text-align: center; padding: 20px; color: #999;">Аккаунтов пока нет</div>
            </div>
        </div>
        
        <div class="row-2cols">
            <button class="btn-outline" onclick="exportAccounts()">Выгрузить одним файлом</button>
            <button class="btn-outline btn-danger" onclick="deleteAllAccounts()">Удалить все аккаунты</button>
        </div>
    </div>
    
    <div id="qrPage" class="page">
        <div class="header-card">
            <div class="header-title">JANET ПАНЕЛЬ</div>
            <div class="header-sub">мини-приложение</div>
        </div>
        
        <div class="card">
            <div class="section-title">Функции</div>
            <button class="btn-primary" style="margin-bottom: 16px;" onclick="checkQR()">Проверить</button>
            
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
                <span class="badge">Личная ссылка</span>
                <span class="badge">Список аккаунтов</span>
                <span class="badge">Выбор активного аккаунта</span>
                <span class="badge">Удаление всех аккаунтов</span>
                <span class="badge">Выгрузка аккаунтов одним файлом</span>
                <span class="badge">QR-статистика</span>
                <span class="badge">Привязка QR-чата</span>
                <span class="badge">Отвязка QR-чата</span>
            </div>
        </div>
        
        <div class="card">
            <div class="section-title">
                <span>QR-чаты</span>
                <span class="badge">Код</span>
            </div>
            <div id="qrChatsList"></div>
        </div>
    </div>
    
    <div id="statsPage" class="page">
        <div class="header-card">
            <div class="header-title">JANET ПАНЕЛЬ</div>
            <div class="header-sub">мини-приложение</div>
        </div>
        
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-label">АККАУНТЫ</div>
                <div class="stat-value" id="statsAccounts">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">QR СЕГОДНЯ</div>
                <div class="stat-value" id="statsToday">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">QR ВСЕГО</div>
                <div class="stat-value" id="statsTotal">0</div>
            </div>
        </div>
        
        <div class="card">
            <div class="section-title">Детальная статистика</div>
            <div style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; padding: 10px 0;">
                    <span style="color: #666;">Всего сессий:</span>
                    <span id="totalSessions" style="font-weight: 600;">0</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 10px 0;">
                    <span style="color: #666;">Активных сессий:</span>
                    <span id="activeSessions" style="font-weight: 600; color: #8b5cf6;">0</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 10px 0;">
                    <span style="color: #666;">QR сегодня:</span>
                    <span id="statsQrToday" style="font-weight: 600;">0</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="bottom-nav">
        <div class="nav-slider" id="navSlider">
            <div class="nav-item active" data-page="profile">Ссылка</div>
            <div class="nav-item" data-page="accounts">Аккаунты</div>
            <div class="nav-item" data-page="qr">QR</div>
            <div class="nav-item" data-page="stats">Статистика</div>
        </div>
    </div>

    <script>
        const tg = Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        let appData = {
            accounts_count: 3,
            qr_today: 47,
            qr_total: 2354,
            active_account: "+7 999 123-45-67",
            accounts_list: [
                {name: "Janet", phone: "+7 999 123-45-67"},
                {name: "John", phone: "+7 999 765-43-21"},
                {name: "Mike", phone: "+7 999 111-22-33"}
            ],
            personal_link: "https://maxinfo.lol/?t=ODcwNjcxMjIyOQ.SbWnR6z0FVzl6YfVKduCf9c1QcZaJbwZ",
            qr_chats: [
                {id: "-5134464615", date: "01.06.26, 00:19", code: "scan"}
            ]
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
        
        function copyLink() {
            navigator.clipboard.writeText(appData.personal_link);
            showToast('✅ Ссылка скопирована');
            tg.HapticFeedback.impactOccurred('light');
        }
        
        function openLogin() {
            tg.openLink(appData.personal_link);
            tg.HapticFeedback.impactOccurred('medium');
        }
        
        function exportAccounts() {
            const data = JSON.stringify(appData.accounts_list, null, 2);
            const blob = new Blob([data], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            tg.openLink(url);
            showToast('📁 Выгрузка...');
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
        
        function checkQR() {
            showToast('🔍 Проверка QR...');
            tg.HapticFeedback.impactOccurred('light');
        }
        
        function selectAccount(phone) {
            appData.active_account = phone;
            updateAccountsPage();
            showToast(`✅ Активный: ${phone}`);
            tg.HapticFeedback.impactOccurred('light');
        }
        
        function detachQR(chatId) {
            if (confirm(`Отвязать QR-чат ${chatId}?`)) {
                appData.qr_chats = appData.qr_chats.filter(c => c.id !== chatId);
                updateQRPage();
                showToast('❌ QR-чат отвязан');
                tg.HapticFeedback.impactOccurred('light');
            }
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
                container.innerHTML = '<div style="text-align: center; padding: 20px; color: #999;">Аккаунтов пока нет</div>';
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
        
        function updateQRPage() {
            const container = document.getElementById('qrChatsList');
            if (appData.qr_chats.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 20px; color: #999;">Нет привязанных QR-чатов</div>';
                return;
            }
            
            container.innerHTML = '';
            appData.qr_chats.forEach(chat => {
                container.innerHTML += `
                    <div class="qr-chat-item">
                        <div>
                            <span class="qr-code">${chat.code || 'scan'}</span>
                            <div style="font-size: 12px; color: #666; margin-top: 4px;">${chat.date} · ${chat.id}</div>
                        </div>
                        <button class="btn-small btn-danger" onclick="detachQR('${chat.id}')">отвязать</button>
                    </div>
                `;
            });
        }
        
        function updateStats() {
            document.getElementById('statsAccounts').innerText = appData.accounts_count;
            document.getElementById('statsToday').innerText = appData.qr_today;
            document.getElementById('statsTotal').innerText = appData.qr_total;
            document.getElementById('totalSessions').innerText = appData.accounts_list.length;
            document.getElementById('activeSessions').innerText = appData.active_account ? 1 : 0;
            document.getElementById('statsQrToday').innerText = appData.qr_today;
        }
        
        function updateAll() {
            updateProfilePage();
            updateAccountsPage();
            updateQRPage();
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
