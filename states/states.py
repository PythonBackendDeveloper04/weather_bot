from aiogram.filters.state import State, StatesGroup

class Form(StatesGroup):
    region = State()
    time = State()

class Form2(StatesGroup):
    region = State()
class Form3(StatesGroup):
    time = State()