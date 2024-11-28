from loader import bot, dp, db,scheduler
import handlers,middlewares
from utils.notify_admins import start,shutdown
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
from utils.set_botcommands import commands
import logging
import sys
import asyncio
from apscheduler.triggers.cron import CronTrigger
from handlers.users.start import scheduled_job

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=commands,scope=BotCommandScopeAllPrivateChats(type='all_private_chats'))
        dp.startup.register(start)
        dp.shutdown.register(shutdown)
        try:
            db.users_table()
        except Exception as e:
            print(e)
        scheduler.add_job(scheduled_job, CronTrigger(hour="*"))
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    asyncio.get_event_loop().run_forever()
