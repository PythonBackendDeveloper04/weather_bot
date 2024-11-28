from aiogram.utils.keyboard import ReplyKeyboardBuilder
def region_keyboard():
    btn = ReplyKeyboardBuilder()
    regions = ["Toshkent", "Andijon", "Buxoro","Guliston","Jizzax","Qarshi","Navoiy","Namangan","Nukus","Samarqand","Termez","Xorazm","Farg'ona"]
    for i in regions:
        btn.button(text=i)
    btn.adjust(1)
    return btn.as_markup(resize_keyboard=True)

def time_keyboard():
    btn = ReplyKeyboardBuilder()
    times = [f"{hour:02}:00" for hour in range(24)]
    for i in times:
        btn.button(text=i)
    btn.adjust(1)
    return btn.as_markup(resize_keyboard=True)

def menu_keyboard():
    btn = ReplyKeyboardBuilder()
    btn.button(text="⛅️ Bugungi ob-havo")
    btn.button(text="⚙️ Botni sozlash")
    btn.button(text="✉️ Murojaat")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)