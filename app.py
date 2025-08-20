# app.py — FastAPI backend for Telegram Mini App (с CORS)
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

# === ТОКЕН БОТА ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА_ЗДЕСЬ")
bot = Bot(BOT_TOKEN)

app = FastAPI(title="MiniApp Backend")

# === CORS: разрешаем запросы с GitHub Pages / Telegram WebView ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # можно сузить до ["https://eternaldesignco.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubmitPayload(BaseModel):
    query_id: str | None = None
    user_id: int | None = None        # запасной путь
    data: dict

@app.get("/")
async def root():
    return {"ok": True, "service": "miniapp-backend"}

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/tma/submit")
async def tma_submit(p: SubmitPayload, request: Request):
    """
    1) Есть p.query_id -> отвечаем через answerWebAppQuery (основной путь)
    2) Иначе, если задан p.user_id -> отправляем личное сообщение пользователю
    """
    text = "✅ Mini App прислал данные:\n" + repr(p.data)

    if p.query_id:
        result = InlineQueryResultArticle(
            id=str(p.data.get("ts", "1")),
            title="Заявка из Mini App",
            input_message_content=InputTextMessageContent(message_text=text),
        )
        await bot.answer_web_app_query(web_app_query_id=p.query_id, result=result)
        return {"ok": True, "via": "answerWebAppQuery"}

    if p.user_id:
        await bot.send_message(chat_id=p.user_id, text=text)
        return {"ok": True, "via": "sendMessage"}

    return {"ok": False, "error": "Either query_id or user_id must be provided"}
