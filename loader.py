from pytz import timezone
from aiogram import Bot,Dispatcher
from data.config import BOT_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from utils.database_manager.sqlite import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
os.environ['TZ'] = 'Asia/Tashkent'
bot = Bot(token=BOT_TOKEN,parse_mode='HTML')
dp = Dispatcher(storage=MemoryStorage())
db = Database(path_to_db='data/main.db')
scheduler = AsyncIOScheduler(timezone=timezone("Asia/Tashkent"))