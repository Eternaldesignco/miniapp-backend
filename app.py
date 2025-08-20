# bot.py — меню слева + приём web_app_data
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import MenuButtonWebApp, WebAppInfo

API_TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН"
MINIAPP_URL = "https://eternaldesignco.github.io/paybot/?v=14"  # увеличил версию

logging.basicConfig(level=logging.INFO)
bot = Bot(API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def on_start(m: types.Message):
    await m.answer("Открывай Mini App через кнопку слева (скрепка → «Открыть Mini App»).")

# ВАЖНО: приём данных от мини-аппа, когда страница использует tg.sendData(...)
@dp.message(F.web_app_data)
async def on_web_app_data(m: types.Message):
    try:
        await m.answer(f"✅ Mini App прислал данные:\n{m.web_app_data.data}")
    except Exception as e:
        await m.answer(f"Не смог прочитать данные: {e!s}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Открыть Mini App",
            web_app=WebAppInfo(url=MINIAPP_URL)
        )
    )
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
