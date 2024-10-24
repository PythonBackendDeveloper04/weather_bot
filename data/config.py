from environs import Env
env = Env()
env.read_env()
BOT_TOKEN=env.str('BOT_TOKEN')
ADMINS=env.list('ADMINS')
WEATHER_API_KEY=env.str("WEATHER_API_KEY")
RAPIDAPIHOST=env.str("RAPIDAPI_HOST")