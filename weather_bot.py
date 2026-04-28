import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

API_TOKEN = '8591307931:AAFy1a_fa3cgW7RS9sm_UWy80zK9rFKJKrs'
CHAT_ID = 1017326410 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def get_weather():
    # Використовуємо інший вузол API для більшої стабільності
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms"
    
    # Максимальна імітація реального браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get('current_weather', {})
                    temp = current.get('temperature')
                    wind = current.get('windspeed')
                    if temp is not None:
                        return f"🌡 Температура: {temp}°C\n💨 Вітер: {wind} м/с"
                return f"Помилка з'єднання (Код: {response.status})"
    except Exception as e:
        return f"Тимчасовий збій метеостанції 🌦"

# Веб-сервер для Render (щоб бот не вимикався)
async def handle(request): return web.Response(text="Bot is Live")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    await web.TCPSite(runner, '0.0.0.0', port).start()

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
    await message.answer("Бот активовано! ✅ Спробую писати сюди щогодини.")

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
