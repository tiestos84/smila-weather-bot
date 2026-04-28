import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# Твій останній робочий токен
API_TOKEN = '8591307931:AAFMIBTeCJMmjueW80nycbAZOWzrz7NK4uk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    res = data.get('current_weather', {})
                    temp = res.get('temperature', '??')
                    wind = res.get('windspeed', '??')
                    return f"📍 Сміла\n\n🌡 Температура: {temp}°C\n💨 Вітер: {wind} м/с"
                return "Сервер погоди тимчасово недоступний ☕"
    except:
        return "Не вдалося отримати дані ❌"

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    weather_info = await get_weather()
    await message.reply(f"Погода у Смілі зараз:\n\n{weather_info}")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот працює! ✅ Напиши /weather для прогнозу.")

# --- Секція для підтримки Render "живим" ---
async def handle(request):
    return web.Response(text="Bot is Alive")

async def main():
    # Запускаємо вебсервер на порту 10000
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()
    
    # Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
