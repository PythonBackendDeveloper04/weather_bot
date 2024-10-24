from loader import dp, bot, db
from aiogram.filters import CommandStart,Command
from aiogram import types,F
from keyboards.default.buttons import region_keyboard, time_keyboard, menu_keyboard
from keyboards.inline.buttons import btn
from aiogram.fsm.context import FSMContext
from states.mystates import Form
from utils.db_api import sqlite
from datetime import datetime, timedelta
import logging
import requests
from data.config import WEATHER_API_KEY,RAPIDAPIHOST
async def get_weather_data(region):
    # Ob-havo ma'lumotlarini olish logikasi
    return f"""<b>🕹Oʻzbekiston {region}</b>
                
📆 Bugun, <b>23-Sentabr 14:44</b>

☀️ Ochiq️ havo, <b>+34°...+22°</b>

🏠 Hozir:️ <b>+33° , 2.06 m/s</b>

⛅ Tong: <b>+22°</b>
🌞 Kunduzi: <b>+33°</b>
🌚 Kechasi:️ <b>+27°</b>

☁️ Bulutlilik: <b>0 %</b>
💧Namlik: <b>17 %</b>
🌬 Shamol: <b>4.43 m/s</b>
🌊 Shamol yo'nalishi: <b>G'arbiy, g'arbi-janub</b>
🌫 Bosim: <b>1012 hPa</b>

🌙 Oy: <b>🌔 Qisqarayotgan oy</b>
🌕 Oy chiqishi: <b>21:49</b>
🌑 Oy botishi: <b>12:31</b>

⛅ Quyosh chiqishi: <b>06:19</b>
🌥 Quyosh botishi: <b>18:26</b>"""
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
async def start(message:types.Message,state:FSMContext):
    await message.answer(text.format(message.from_user.first_name))
    await message.answer("Qaysi tumandansiz?",reply_markup=region_keyboard())
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

@dp.message(F.text=="📉 Haftalik ma'lumot")
async def haftalik_ob_havo(message:types.Message):
    users_data = db.select_all_user()
    for id, telegram_id, region, time in users_data:
        if message.from_user.id == telegram_id:
            url = "https://open-weather-map27.p.rapidapi.com/weather"

            querystring = {"q": region, "units": "metric"}  # Shahar va o'lchov birligini qo'shish

            headers = {
                "x-rapidapi-key": "6d6ecef7e9mshd3be8d28211f6afp12e196jsnf36f9bf90211",
                "x-rapidapi-host": "open-weather-map27.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=querystring)

            if response.status_code == 200:
                data = response.json()
                weather_info = [f"🕹 Oʻzbekiston Surxondaryo Viloyati Termiz Tumani\n"]

                # Ma'lumotlarni olish
                description = data['weather'][0]['description'].capitalize()
                temp = data['main']['temp']
                temp_min = data['main']['temp_min']
                temp_max = data['main']['temp_max']
                rain_chance = data.get('pop', 0) * 100  # Yog'ish ehtimolligini olish (agar mavjud bo'lsa)

                # Natijalarni formatlash
                weather_info.append(f"☀️ {description} havo, +{temp_max:.0f}°...+{temp_min:.0f}°\n"
                                    f"☔️ Yog'ish ehtimolligi: {rain_chance:.0f}%\n")

                await message.answer("\n".join(weather_info))
            else:
                await message.answer(
                    f"Ob-havo ma'lumotlarini olishda xato yuz berdi. Status kod: {response.status_code}\nXato: {response.text}")