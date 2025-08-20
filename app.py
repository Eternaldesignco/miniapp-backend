import os, uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, types
from aiogram.exceptions import TelegramAPIError

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is not set")

bot = Bot(BOT_TOKEN)
app = FastAPI()

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
    try:
        me = await bot.get_me()
        return {"ok": True, "bot": f"@{me.username}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/tma/submit")
async def submit(p: Payload):
    try:
        result = types.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="Заявка получена",
            input_message_content=types.InputTextMessageContent(
                message_text=f"✅ Mini App прислал данные:\n{p.data}"
            ),
        )
        await bot.answer_web_app_query(p.query_id, result)
        return {"ok": True}
    except TelegramAPIError as e:
        raise HTTPException(status_code=400, detail=f"telegram_error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"server_error: {e}")
