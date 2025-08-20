import os
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiogram import Bot, types

BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # на Render задай BOT_TOKEN
bot = Bot(token=BOT_TOKEN)
app = FastAPI()

@app.get("/")
async def root():
    return {"ok": True, "service": "miniapp-backend", "version": 2}

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/tma/submit")
async def submit(req: Request):
    try:
        body = await req.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "bad json"}, status_code=400)

    data = body.get("data") or {}
    query_id = body.get("query_id")
    user_id = body.get("user_id")

    # что отправим в телеграм
    text = (
        "✅ Mini App прислал данные:\n"
        f"{data}"
    )

    # 1) если пришёл query_id — значит webapp открыт из inline-кнопки
    if query_id:
        try:
            result = types.InlineQueryResultArticle(
                id=str(uuid4()),
                title="Заявка отправлена",
                input_message_content=types.InputTextMessageContent(text)
            )
            await bot.answer_web_app_query(web_app_query_id=query_id, result=result)
            return {"ok": True, "via": "answerWebAppQuery"}
        except Exception as e:
            return JSONResponse({"ok": False, "error": f"aq: {e}"}, status_code=500)

    # 2) иначе — пришлём сообщение пользователю напрямую
    if user_id:
        try:
            await bot.send_message(chat_id=int(user_id), text=text)
            return {"ok": True, "via": "sendMessage"}
        except Exception as e:
            return JSONResponse({"ok": False, "error": f"sm: {e}"}, status_code=500)

    return JSONResponse({"ok": False, "error": "no query_id or user_id"}, status_code=400)
