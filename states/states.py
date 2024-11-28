from aiogram.filters.state import State, StatesGroup

class Form(StatesGroup):
    region = State()
    time = State()