import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# ТОКЕНИ
API_TOKEN = '8591307931:AAFMIBTeCJMmjueW80nycbAZOWzrz7NK4uk'
WEATHER_API_KEY = 'E49PLLVDESY9FUXGHGGL2XXG6'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def get_weather():
    # Запит для Сміли через Visual Crossing API
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Smila,UA/today?unitGroup=metric&key={WEATHER_API_KEY}&contentType=json&lang=uk"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data['currentConditions']
                    
                    temp = current.get('temp', '??')
                    desc = current.get('conditions', 'Без опису')
                    wind = current.get('windspeed', '??')
                    humidity = current.get('humidity', '??')
                    
                    return (f"📍 Сміла (Visual Crossing)\n\n"
                            f"🌡 Температура: {temp}°C\n"
                            f"☁️ Стан: {desc}\n"
                            f"💧 Вологість: {humidity}%\n"
                            f"💨 Вітер: {wind} км/год")
                else:
                    return "Сервер погоди зайнятий, спробуйте пізніше 🛑"
    except Exception as e:
        return "Помилка зв'язку з метеостанцією ❌"

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    weather_info = await get_weather()
    await message.reply(weather_info)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот оновлений! ✅ Тепер я використовую професійні дані Visual Crossing. Напиши /weather")

# Веб-сервер для стабільності на Render
async def handle(request):
    return web.Response(text="Weather Bot is online and healthy")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
