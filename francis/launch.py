import discord
# import asyncio

from config import BOT_TOKEN
from discord.ext import commands
from discord.errors import HTTPException
from utils import Utility
from cogs import role, help, link, admin, requirement, tasks, webspiders
import config

if config.DEBUG is True:
    prefix = '.'
else:
    prefix = '!'

bot = commands.Bot(command_prefix=prefix, description='Francis - Orchid\'s slave')
# remove the 'help' command
bot.remove_command('help')

# initialize bot's utility functions
util = Utility(bot)

# add Role cog to the bot
bot.add_cog(role.Role(bot, util))
bot.add_cog(help.Help(bot, util))
bot.add_cog(link.Link(bot, util))
bot.add_cog(admin.Admin(bot, util))
bot.add_cog(requirement.Requirement(bot, util))

# EVENTS


@bot.event
async def on_ready():
    print('------')
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')
    print('------')
    if not config.DEBUG:
        await bot.change_presence(game=discord.Game(name=f'{bot.command_prefix}help'))


@bot.event
async def on_member_join(member):
    """Says when a member joined."""

    if not config.DEBUG:
        welcome_channel = discord.utils.get(member.server.channels, name='welcome')
        rules_channel = discord.utils.get(member.server.channels, name='nội-quy')
        message = f'Chào mừng **{member.mention}** đã đến với **{member.server.name}**!\n\
    Bạn vui lòng đọc Nội quy ở {rules_channel.mention} nhé.'

        await bot.send_message(welcome_channel, message)


@bot.event
async def on_message(message):
    server = message.server

    if server is None:
        try:
            await bot.send_message(
                destination=message.author,
                content=f'Bạn vui lòng quay lại group **Cộng đồng MapleStory VN** và nhập lệnh `{bot.command_prefix}help` '
                'nhé. Xin cảm ơn :D')
        except HTTPException:
            pass
    else:
        role_request_channel = server.get_channel('453930352365273099')  # yêu-cầu-role

        if message.channel == role_request_channel and message.content.startswith(bot.command_prefix):
            await bot.delete_message(message)
        else:
            await bot.process_commands(message)

twitter_tasks = tasks.Twitter(bot, util)
facebook_tasks = tasks.Facebook(bot, util)

bot.loop.create_task(twitter_tasks.fetch_maplem_latest_tweet())
bot.loop.create_task(twitter_tasks.fetch_maple_latest_tweet())
bot.loop.create_task(webspiders.WebSpider(bot, util).parse())


if config.DEBUG:
    # bot.loop.create_task(facebook_tasks.fb())
    bot.loop.create_task(webspiders.WebSpider(bot, util).parse())

bot.run(BOT_TOKEN)
