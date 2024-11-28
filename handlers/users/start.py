from loader import dp, bot, db
from aiogram.filters import CommandStart
from aiogram import types,F
from keyboards.default.buttons import region_keyboard, time_keyboard, menu_keyboard
from keyboards.inline.buttons import btn
from aiogram.fsm.context import FSMContext
from states.states import Form
from datetime import datetime
import requests
from data.config import WEATHER_API_KEY

async def get_weather_data(region):
    url = "http://api.weatherstack.com/current"
    params = {
        "access_key": WEATHER_API_KEY,
        "query": region,
        "units": "m",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        description = data['current']['weather_descriptions'][0].capitalize()
        temp = data['current']['temperature']
        temp_min = temp - 5
        temp_max = temp + 5
        humidity = data['current']['humidity']
        wind_speed = data['current']['wind_speed']
        wind_dir = data['current']['wind_degree']
        pressure = data['current']['pressure']

        def get_uzbek_month_name(month_num):
            months = {
                1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
                7: "Iyul", 8: "Avgust", 9: "Sentabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr"
            }
            return months.get(month_num, "")

        now = datetime.now()
        month_name = get_uzbek_month_name(now.month)

        weather_message = f"""
            <b>🕹 Oʻzbekiston {region}</b>

📆 Bugun, <b>{now.day}-{month_name} {now.strftime('%H:%M')}</b>
☀️ {description} havo, <b>+{temp_max}°...+{temp_min}°</b>

🏠 Hozir:️ <b>+{temp}° , {wind_speed} m/s</b>

⛅ Tong: <b>+{temp_min}°</b>
🌞 Kunduzi: <b>+{temp_max}°</b>
🌚 Kechasi:️ <b>+{temp - 2}°</b>

☁️ Bulutlilik: <b>{data['current']['cloudcover']} %</b>
💧 Namlik: <b>{humidity} %</b>
🌬 Shamol: <b>{wind_speed} m/s</b>
🌊 Shamol yo'nalishi: <b>{wind_dir}°</b>
🌫 Bosim: <b>{pressure} hPa</b>
        """
        return weather_message
    else:
        return "Ob-havo ma'lumotlarini olishda xatolik yuz berdi."


async def send_message(user_id, region):
    weather_data = await get_weather_data(region)
    await bot.send_message(user_id, weather_data)

async def scheduled_job():
    users_data = db.select_all_user()
    for id, telegram_id, region, time in users_data:
        current_time = datetime.now().strftime("%H:%M")
        if current_time == time:
            await send_message(telegram_id, region)  # Foydalanuvchiga xabar yuborish

text = """
<b>Assalomu Aleykum, {}

🚀 Ob havo botiga xush kelibsiz, Bot orqali O'zbekistonning barcha hududlaridagi ob-havo ma'lumotini ko'rishingiz mumkin.

Bot orqali siz, hududingizdagi 2 xil obhavo ma'lumotini bilishingiz mumkin

1️⃣ Hozirgi ob-havo (to'liq ma'lumot)
2️⃣ Haftalik ob-havo</b>
"""

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    # Foydalanuvchini bazadan tekshirish
    user_data = db.select_user(message.from_user.id)
    print(user_data)
    if user_data:
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa
        region = user_data["region"]
        time = user_data["time"]
        await message.answer(
            f"Assalomu alaykum, {message.from_user.first_name}!\n"
            f"Siz allaqachon quyidagi ma'lumotlarni saqlagansiz:\n"
            f"📍 Manzil: <b>{region}</b>\n"
            f"⏰ Vaqt: <b>{time}</b>\n\n"
            f"Qo'shimcha sozlamalar uchun '⚙️ Botni sozlash' tugmasidan foydalanishingiz mumkin.",
            reply_markup=menu_keyboard(),
        )
    else:
        # Agar foydalanuvchi bazada bo'lmasa, yangi ma'lumotlarni so'rash
        await message.answer(text.format(message.from_user.first_name))
        await message.answer("Qaysi tumandansiz?", reply_markup=region_keyboard())
        await state.set_state(Form.region)


@dp.message(lambda message: message.text in ["Toshkent", "Andijon", "Buxoro","Guliston","Jizzax","Qarshi","Navoiy","Namangan","Nukus","Samarqand","Termez","Xorazm","Farg'ona"],Form.region)
async def process_region(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data({
        "region":region
    })
    await state.set_state(Form.time)
    await message.answer("Qaysi vaqtda ob-havo ma'lumotlarini olishni istaysiz? (00:00 dan 23:00 gacha):", reply_markup=time_keyboard())


@dp.message(lambda message: message.text.startswith("0") or message.text.startswith("1") or message.text.startswith("2"),Form.time)
async def process_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    region = user_data['region']
    time = message.text

    db.add_user(telegram_id=message.from_user.id,region=region,time=time)

    await message.answer(f"Endi sizga har kuni soat {time} da {region} bo'yicha ob-havo ma'lumotlarini yuboraman.",reply_markup=menu_keyboard())
    await state.clear()
@dp.message(F.text=="⛅️ Bugungi ob-havo")
async def bugungi_ob_havo(message:types.Message):
    users_data = db.select_all_user()
    for id, telegram_id, region, time in users_data:
        await send_message(telegram_id, region)

user_info = """
👤 Sizning sozlamalaringiz:

Manzil: <b>{}</b>
Vaqt: <b>{}</b>
Til: <b>{}</b>
"""

@dp.message(F.text=="⚙️ Botni sozlash")
async def settings(message:types.Message):
    users_data = db.select_all_user()
    for id, telegram_id, region, time in users_data:
        if message.from_user.id == telegram_id:
            await message.answer(user_info.format(region,time,"Uz"))
            break

@dp.message(F.text == "✉️ Murojaat")
async def murojaat(message:types.Message):
    await message.answer("🤖Bot faoliyati boʻyicha taklif yoki savollaringiz boʻlsa, bemalol Administrator ga yozishingiz mumkin.😉",reply_markup=btn.as_markup())