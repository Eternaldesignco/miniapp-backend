# app.py  — FastAPI backend for Telegram Mini App
import os
from fastapi import FastAPI
from pydantic import BaseModel
from aiogram import Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

# ====== токен бота ======
BOT_TOKEN = os.getenv("BOT_TOKEN", "7681232671:AAE...твой_токен...")
bot = Bot(BOT_TOKEN)

app = FastAPI(title="MiniApp Backend")

class SubmitPayload(BaseModel):
    query_id: str | None = None
    user_id: int | None = None            # для фолбэка/тестов
    data: dict

@app.get("/")
async def root():
    return {"ok": True, "service": "miniapp-backend"}

@app.post("/tma/submit")
async def tma_submit(p: SubmitPayload):
    """
    Два пути:
    1) p.query_id -> answerWebAppQuery (основной путь, когда открыли через Main App / Direct Link)
    2) иначе (для тестов) p.user_id -> sendMessage пользователю
    """
    text = (
        "✅ Mini App прислал данные:\n"
        f"{p.data!r}"
    )

    # 1) Основной путь — ответить через answerWebAppQuery
    if p.query_id:
        result = InlineQueryResultArticle(
            id=str(p.data.get("ts", "1")),
            title="Заявка из Mini App",
            input_message_content=InputTextMessageContent(message_text=text)
        )
        await bot.answer_web_app_query(web_app_query_id=p.query_id, result=result)
        return {"ok": True, "via": "answerWebAppQuery"}

    # 2) Фолбэк — отправить личное сообщение пользователю
    if p.user_id:
        await bot.send_message(chat_id=p.user_id, text=text)
        return {"ok": True, "via": "sendMessage"}

    return {"ok": False, "error": "Either query_id or user_id must be provided"}
