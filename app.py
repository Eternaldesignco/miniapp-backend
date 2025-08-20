import os
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from aiogram.client.bot import Bot
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

# ---- конфиг
BOT_TOKEN = os.getenv("BOT_TOKEN")  # задашь в Render → Environment
bot = Bot(BOT_TOKEN)

app = FastAPI()

# входные данные
class SubmitPayload(BaseModel):
    query_id: str          # обязателен при открытии через кнопку слева/меню
    data: dict             # любая твоя полезная нагрузка (имя/тел/коммент)
    user_id: int | None = None  # можно не присылать

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("OK")

@app.post("/tma/submit")
async def tma_submit(p: SubmitPayload):
    """
    Возвращаем сообщение в чат через answerWebAppQuery.
    Работает только если query_id прислан из Mini App.
    """
    if not BOT_TOKEN:
        return JSONResponse({"ok": False, "error": "No BOT_TOKEN set"}, status_code=500)
    if not p.query_id:
        return JSONResponse({"ok": False, "error": "query_id is empty"}, status_code=400)

    text = "✅ Mini App прислал данные:\n" + json.dumps(
        p.data, ensure_ascii=False, indent=2
    )

    try:
        await bot.answer_web_app_query(
            web_app_query_id=p.query_id,
            result=InlineQueryResultArticle(
                id="ok",
                title="Заявка отправлена",
                input_message_content=InputTextMessageContent(text)
            ),
        )
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
