import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime

# Твій особистий токен
API_TOKEN = '8591307931:AAFy1a_fa3cgW7RS9sm_UWy80zK9rFKJKrs'
# Сюди бот автоматично запише твій ID
USER_ID = None 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_weather():
    """Отримання даних через Open-Meteo API"""
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.23&longitude=31.88&current_weather=true&windspeed_unit=ms&timezone=auto"
    try:
        response = requests.get(url).json()
        res = response['current_weather']
        w_map = {
            0: "Ясно ☀️", 1: "Переважно ясно 🌤", 2: "Мінлива хмарність ⛅", 
            3: "Хмарно ☁️", 45: "Туман 🌫", 51: "Легка мряка 🌧", 
            61: "Дощ 🌦", 71: "Сніг ❄️", 95: "Гроза ⛈"
        }
        status = w_map.get(res['weathercode'], 'Змішані умови ⛅')
        return f"🌡 Температура: **{res['temperature']}°C**\n☁️ Стан: **{status}**\n💨 Вітер: **{res['windspeed']} м/с**"
    except:
        return None

async def send_daily_weather():
    """Функція, яка перевіряє час і відправляє повідомлення о 07:15"""
    while True:
        now = datetime.now()
        # Перевіряємо, чи зараз 07:15
        if now.hour == 7 and now.minute == 15:
            if USER_ID:
                weather = get_weather()
                if weather:
                    try:
                        await bot.send_message(
                            USER_ID, 
                            f"Доброго ранку! ☕\nОсь погода у Смілі на сьогодні (07:15):\n\n{weather}", 
                            parse_mode="Markdown"
                        )
                        print(f"[{now.strftime('%H:%M')}] Розсилка відправлена успішно.")
                    except Exception as e:
                        print(f"Помилка відправки: {e}")
            # Чекаємо хвилину, щоб не відправляти кілька разів в одну й ту ж хвилину
            await asyncio.sleep(61) 
        
        # Перевірка кожні 30 секунд
        await asyncio.sleep(30)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global USER_ID
    USER_ID = message.from_user.id
    kb = [[types.KeyboardButton(text="Погода у Смілі 🌦")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        "Бот активований! ✅\nКожного ранку о **07:15** ти отримуватимеш прогноз.\n\n"
        "Важливо: не закривай програму на комп'ютері!", 
        reply_markup=keyboard
    )

@dp.message(lambda m: m.text == "Погода у Смілі 🌦")
async def manual_weather(message: types.Message):
    weather = get_weather()
    if weather:
        await message.answer(
            f"📍 **Сміла**\n\n{weather}\n\n🕒 {datetime.now().strftime('%H:%M')}", 
            parse_mode="Markdown"
        )

async def main():
    print("Бот запущений! Очікую 07:15 для автоматичної розсилки.")
    # Запускаємо фонову задачу для перевірки часу
    asyncio.create_task(send_daily_weather())
    # Запускаємо самого бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот зупинений.")