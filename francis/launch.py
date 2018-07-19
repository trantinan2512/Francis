import discord
# import json
# import asyncio
# from datetime import datetime
# import re
# from discord.ext import commands
from discord.errors import HTTPException

from francis import bot

from francis.cogs import tasks, webspiders, scheduler
import config

if config.DEBUG is True:
    prefix = '.'
else:
    prefix = '!'


francis = bot.FrancisBot(command_prefix=prefix, description='Francis - Orchid\'s slave')
# remove the 'help' command
francis.remove_command('help')

# initialize francis's utility functions
# util = Utility(francis)

initial_extensions = (

    'francis.cogs.admin',
    'francis.cogs.help',
    'francis.cogs.link',
    'francis.cogs.requirement',
    'francis.cogs.role',
)
for extension in initial_extensions:
    try:
        francis.load_extension(extension)
    except Exception as e:
        print(f'Failed to load extension {extension}. Exception: "{e}"')


# EVENTS

@francis.event
async def on_ready():
    print('------')
    print(f'Logged in as: {francis.user.name} (ID: {francis.user.id})')
    print('------')
    if not config.DEBUG:
        await francis.change_presence(game=discord.Game(name=f'{francis.command_prefix}help << hàng thật'))

    # sv = francis.get_server(id='364323564737789953')
    # for role in sv.roles:
    #     print(role.id)
    #     print(role.name)
    #     print('---')


@francis.event
async def on_member_join(member):
    """Says when a member joined."""

    if not config.DEBUG:

        server = member.server
        welcome_channel = server.get_channel('453886339570597890')
        rules_channel = server.get_channel('453566033190584321')
        intro_channel = server.get_channel('455025500071526401')
        francis_channel = server.get_channel('454310191962390529')

        message = (
            f'Chào mừng **{member.mention}** đã đến với **{member.server.name}**!\n\n' +
            f'Dưới đây là hướng dẫn tương tác với group nhé!\n' +
            f'» Đọc {rules_channel.mention} ở đây.\n' +
            f'» {intro_channel.mention} giới thiệu bản thân.\n' +
            f'» Qua {francis_channel.mention} để thêm Role cho mình, mở thêm các kênh chat và kênh tin tức cho game!\n\n' +
            f'Nhập lệnh `{francis.command_prefix}help` để được hỗ trợ thêm nhé.')

        await francis.send_message(welcome_channel, message)


@francis.event
async def on_message(message):
    server = message.server

    if server is None:
        try:
            await francis.send_message(
                destination=message.author,
                content=f'Bạn vui lòng quay lại group **Cộng đồng MapleStory VN** và nhập lệnh `{francis.command_prefix}help` '
                'nhé. Xin cảm ơn :D')
        except HTTPException:
            pass
    else:
        role_request_channel = server.get_channel('453930352365273099')

        if message.channel == role_request_channel and message.content.startswith(francis.command_prefix):
            await francis.delete_message(message)

        else:
            await francis.process_commands(message)

if not config.DEBUG:
    francis.loop.create_task(webspiders.WebSpider(francis).parse())
    francis.loop.create_task(tasks.Twitter(francis).fetch_maple_latest_tweet())
    francis.loop.create_task(tasks.Twitter(francis).fetch_maplem_latest_tweet())
    francis.loop.create_task(scheduler.Scheduler(francis).check_gms_schedule())
    francis.loop.create_task(scheduler.Scheduler(francis).check_gmsm_schedule())
    francis.loop.create_task(scheduler.Scheduler(francis).check_dawn_schedule())

if config.DEBUG:
    francis.loop.create_task(webspiders.WebSpider(francis).parse())

francis.run(config.FRANCIS_TOKEN)
