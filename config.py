from decouple import config

BOT_TOKEN = config('BOT_TOKEN')
MY_ID = config('MY_ID', cast=str)
SERVER_ID = config('SERVER_ID', cast=str)
