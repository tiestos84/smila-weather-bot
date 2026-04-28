import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

API_TOKEN = '8591307931:AAFMIBTeCJMmjueW80nycbAZOWzrz7NK4uk'
CHAT_ID = 1017326410 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms"
    headers = {'User-Agent': 'SmilaWeatherBot/1.0'}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    res = data.get('current_weather', {})
                    return f"🌡 Температура: {res.get('temperature')}°C\n💨 Вітер: {res.get('windspeed')} м/с"
                elif response.status == 429:
                    return "Сервер погоди відпочиває. Спробуйте через 5 хвилин ☕"
                else:
                    return f"Статус сервера: {response.status} 🌦"
    except:
        return "Не вдалося отримати дані ❌"

# Веб-сервер для стабільності на Render
async def handle(request): return web.Response(text="Бот активний")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000))).start()

# Автоматична розсилка (щогодини)
async def hourly_broadcast():
    while True:
        await asyncio.sleep(3600)
        weather_text = await get_weather()
        try:
            await bot.send_message(CHAT_ID, f"📢 Щогодинний звіт:\n\n{weather_text}")
        except: pass

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    await message.answer("Бот активовано! ✅ Буду писати сюди щогодини.")

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
