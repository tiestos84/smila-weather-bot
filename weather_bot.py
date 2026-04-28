import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# 1. Твій токен
API_TOKEN = '8591307931:AAFy1a_fa3cgW7RS9sm_UWy80zK9rFKJKrs'
CHAT_ID = 1017326410 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 2. Оновлена функція погоди (надійніша)
async def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms&timezone=auto"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    res = data['current_weather']
                    return f"🌡 Температура: {res['temperature']}°C\n💨 Вітер: {res['windspeed']} м/с"
                else:
                    return "Помилка сервера погоди 🌦"
    except Exception as e:
        return f"Помилка зв'язку ❌"

# 3. Веб-сервер для Render
async def handle(request):
    return web.Response(text="Бот працює!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()

# 4. Щогодинна розсилка
async def hourly_broadcast():
    while True:
        await asyncio.sleep(3600)
        weather_text = await get_weather()
        try:
            await bot.send_message(CHAT_ID, f"📢 Щогодинний звіт:\n\n{weather_text}")
        except:
            pass

# 5. Обробка команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    await message.answer("Бот активовано! ✅ Буду писати щогодини сюди.")

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    weather_info = await get_weather()
    await message.reply(f"Погода у Смілі зараз:\n\n{weather_info}")

async def main():
    asyncio.create_task(start_web_server())
    asyncio.create_task(hourly_broadcast())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
