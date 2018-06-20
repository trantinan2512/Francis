# import discord
# import asyncio
import json
import discord
from discord.ext import commands
from discord.errors import HTTPException
from utils import db, channel as ch
import config

from oz.events import match_word_event

if config.DEBUG is True:
    prefix = '.'
else:
    prefix = '='

oz = commands.Bot(command_prefix=prefix, description='Oz is here for Exploooooosioon')
# remove the 'help' command
oz.remove_command('help')

# EVENTS


@oz.event
async def on_ready():
    print('------')
    print(f'Logged in as: {oz.user.name} (ID: {oz.user.id})')
    print('------')
    if not config.DEBUG:
        await oz.change_presence(game=discord.Game(name=f'Quản trò #match_word'))

valid_words = json.load(open(config.BASE_DIR + '/oz/words_dictionary.json'))
dbe = db.initialize_db()
event_db = dbe.worksheet('match_word_event')


@oz.event
async def on_message(message):
    server = message.server

    if server is None:
        try:
            await oz.send_message(
                destination=message.author,
                content=f'Bạn vui lòng quay lại group **Cộng đồng MapleStory VN** và nhập lệnh `{oz.command_prefix}help` '
                'nhé. Xin cảm ơn :D')
        except HTTPException:
            pass
    else:
        role_request_channel = server.get_channel('453930352365273099')
        match_word_channel = ch.get_channel(server, id='458260628876951552')

        if message.channel == role_request_channel and message.content.startswith(oz.command_prefix):
            await oz.delete_message(message)

        # proc event
        elif message.channel == match_word_channel and message.content.startswith('>'):

            await match_word_event(message, match_word_channel, oz, event_db, valid_words)

        else:
            await oz.process_commands(message)

oz.run(config.OZ_TOKEN)
