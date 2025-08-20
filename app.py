# app.py — FastAPI endpoint для Mini App (Menu Button) через answerWebAppQuery
import os, uuid
from fastapi import FastAPI
from pydantic import BaseModel
from aiogram import Bot, types

BOT_TOKEN = os.environ["BOT_TOKEN"]  # токен зададим на хостинге как переменную окружения
bot = Bot(BOT_TOKEN)
app = FastAPI()

class Payload(BaseModel):
    query_id: str
    data: dict

@app.post("/tma/submit")
async def submit(p: Payload):
    # Отправим в чат сообщение "от имени пользователя", который открыл мини-апп
    result = types.InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="Заявка получена",
        input_message_content=types.InputTextMessageContent(
            message_text=f"✅ Mini App прислал данные:\n{p.data}"
        ),
    )
    await bot.answer_web_app_query(p.query_id, result)
    return {"ok": True}
