import os
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot, types

# ==== токен бота (в Render -> Environment -> BOT_TOKEN) ====
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None

app = FastAPI()

# ==== CORS: разрешаем вызовы из WebView Telegram ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # можно сузить до ["https://web.telegram.org", ...]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"ok": True, "service": "miniapp-backend", "version": 3}

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/tma/submit")
async def submit(req: Request):
    # Проверим токен сразу, чтобы не было молчаливых сбоев
    if not bot:
        return JSONResponse(
            {"ok": False, "error": "BOT_TOKEN is empty on server"},
            status_code=500,
        )

    try:
        body = await req.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "bad json"}, status_code=400)

    data = body.get("data") or {}
    query_id = body.get("query_id")
    user_id = body.get("user_id")

    text = "✅ Mini App прислал данные:\n" + str(data)

    # 1) Если есть query_id — отвечаем через answerWebAppQuery
    if query_id:
        try:
            result = types.InlineQueryResultArticle(
                id=str(uuid4()),
                title="Заявка отправлена",
                input_message_content=types.InputTextMessageContent(text),
            )
            await bot.answer_web_app_query(web_app_query_id=query_id, result=result)
            return {"ok": True, "via": "answerWebAppQuery"}
        except Exception as e:
            return JSONResponse({"ok": False, "error": f"aq: {e}"}, status_code=500)

    # 2) Иначе — шлём в личку пользователю (если передан user_id)
    if user_id:
        try:
            await bot.send_message(chat_id=int(user_id), text=text)
            return {"ok": True, "via": "sendMessage"}
        except Exception as e:
            return JSONResponse({"ok": False, "error": f"sm: {e}"}, status_code=500)

    return JSONResponse(
        {"ok": False, "error": "no query_id or user_id"},
        status_code=400,
    )
