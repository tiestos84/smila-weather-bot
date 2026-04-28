import asyncio
import requests
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime
from aiohttp import web

# Токен вашого бота
API_TOKEN = '8591307931:AAFy1a_fa3cgW7RS9sm_UWy80zK9rFKJKrs'
# Твій ID (щоб бот знав, куди писати о 07:15)
USER_ID = 1017326410 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Веб-сервер для Render ---
async def handle(request):
    return web.Response(text="Бот активний!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- Погода ---
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms&timezone=auto"
    try:
        response = requests.get(url).json()
        res = response['current_weather']
        w_map = {0: "Ясно ☀️", 1: "Переважно ясно 🌤", 2: "Мінлива хмарність ⛅", 3: "Хмарно ☁️", 61: "Дощ 🌦", 71: "Сніг ❄️"}
        status = w_map.get(res['weathercode'], 'Умови мінливі ⛅')
        return f"🌡 Температура: **{res['temperature']}°C**\n☁️ Стан: **{status}**"
    except:
        return None

async def send_daily_weather():
    while True:
        now = datetime.now()
        # 07:15 за Києвом (якщо на сервері UTC, це може бути 04:15)
        if (now.hour == 7 and now.minute == 15) or (now.hour == 4 and now.minute == 15):
            if USER_ID:
                weather = get_weather()
                if weather:
                    try:
                        await bot.send_message(USER_ID, f"Ранковий прогноз: \n\n{weather}", parse_mode="Markdown")
                    except:
                        pass
            await asyncio.sleep(61)
        await asyncio.sleep(30)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот працює на сервері! ✅")

async def main():
    asyncio.create_task(start_web_server())
    asyncio.create_task(send_daily_weather())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
