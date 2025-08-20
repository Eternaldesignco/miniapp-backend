# app.py — FastAPI endpoint для Mini App (Menu Button) через answerWebAppQuery
import os, uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, types

BOT_TOKEN = os.environ["BOT_TOKEN"]  # задаёшь на хостинге
bot = Bot(BOT_TOKEN)

app = FastAPI()

# --- ВАЖНО: разрешаем CORS, иначе fetch из WebApp может падать ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    query_id: str
    data: dict

@app.get("/ping")
async def ping():
    return {"ok": True}

@app.post("/tma/submit")
async def submit(p: Payload):
    # Сообщение «от имени пользователя», открывшего мини-апп
    result = types.InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="Заявка получена",
        input_message_content=types.InputTextMessageContent(
            message_text=f"✅ Mini App прислал данные:\n{p.data}"
        ),
    )
    await bot.answer_web_app_query(p.query_id, result)
    return {"ok": True}
