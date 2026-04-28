import asyncio
import requests
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime
from aiohttp import web

# Токен вашого бота
API_TOKEN = '8591307931:AAFy1a_fa3cgW7RS9sm_UWy80zK9rFKJKrs'
# Твій ID для особистої розсилки (залишаємо як було)
USER_ID = 1017326410 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Веб-сервер для стабільної роботи на Render ---
async def handle(request):
    return web.Response(text="Бот працює!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- Функція отримання даних про погоду ---
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms&timezone=auto"
    try:
        response = requests.get(url).json()
        res = response['current_weather']
        w_map = {
            0: "Ясно ☀️", 1: "Переважно ясно 🌤", 2: "Мінлива хмарність ⛅", 
            3: "Хмарно ☁️", 45: "Туман 🌫", 48: "Паморозь 🌫",
            61: "Невеликий дощ 🌧", 63: "Дощ 🌧", 65: "Сильний дощ 🌧",
            71: "Сніг ❄️", 73: "Снігопад ❄️", 75: "Сильний сніг ❄️",
            80: "Злива ⛈", 95: "Гроза ⚡"
        }
        status = w_map.get(res['weathercode'], 'Умови мінливі ⛅')
        return f"🌡 Температура: **{res['temperature']}°C**\n☁️ Стан: **{status}**"
    except:
        return None

# --- Автоматична розсилка о 07:15 ---
async def send_daily_weather():
    while True:
        now = datetime.now()
        # Перевірка часу (7:15 за Києвом або 4:15 за UTC на сервері)
        if (now.hour == 7 and now.minute == 15) or (now.hour == 4 and now.minute == 15):
            if USER_ID:
                weather = get_weather()
                if weather:
                    try:
                        await bot.send_message(USER_ID, f"Ранковий прогноз погоди у Смілі: \n\n{weather}", parse_mode="Markdown")
                    except:
                        pass
            await asyncio.sleep(61)
        await asyncio.sleep(30)

# --- Команда /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот запущений! ✅\n\nВикористовуй команду /weather, щоб дізнатися погоду прямо зараз.")

# --- НОВА КОМАНДА: /weather (працює і в групах) ---
@dp.message(Command("weather"))
async def get_weather_on_demand(message: types.Message):
    weather = get_weather()
    if weather:
        await message.answer(f"Погода у Смілі зараз:\n\n{weather}", parse_mode="Markdown")
    else:
        await message.answer("Не вдалося отримати дані. Спробуйте пізніше. 😔")

# --- Головна функція запуску ---
async def main():
    # Запускаємо сервер для Render, щоб бот не "засинав"
    asyncio.create_task(start_web_server())
    # Запускаємо таймер розсилки
    asyncio.create_task(send_daily_weather())
    # Запускаємо прослуховування повідомлень
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
