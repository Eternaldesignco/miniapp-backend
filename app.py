import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

# ==== ТВОЙ ТОКЕН БОТА (вшит) ====
BOT_TOKEN = os.getenv("BOT_TOKEN", "7681232671:AAEVffXef-YtxpRLHbohNh00kg7Qj2lg-U0")

bot = Bot(token=BOT_TOKEN, parse_mode=None)

app = FastAPI()

# CORS — чтобы GitHub Pages мог обращаться к Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # при желании сузишь до своего GH Pages
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

class SubmitPayload(BaseModel):
    query_id: str
    data: dict

@app.get("/")
async def root():
    return {"ok": True, "ping": "pong"}

@app.post("/tma/submit")
async def submit(payload: SubmitPayload):
    if not payload.query_id:
        raise HTTPException(status_code=400, detail="query_id is required (open inside Telegram)")

    text = f"✅ Mini App прислал данные:\n{payload.data}"

    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title="Заявка принята",
        input_message_content=InputTextMessageContent(message_text=text),
    )

    # Ключевой ответ — сообщение от бота в чат, инициированное Mini App
    await bot.answer_web_app_query(web_app_query_id=payload.query_id, result=result)

    return {"ok": True}
