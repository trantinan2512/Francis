import discord
import asyncio
from datetime import datetime
import re

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

        server = member.server
        welcome_channel = server.get_channel('453886339570597890')
        rules_channel = server.get_channel('453566033190584321')
        intro_channel = server.get_channel('455025500071526401')
        bot_channel = server.get_channel('454310191962390529')

        message = (
            f'Chào mừng **{member.mention}** đã đến với **{member.server.name}**!\n\n' +
            f'Dưới đây là hướng dẫn tương tác với group nhé!\n' +
            f'» Đọc {rules_channel.mention} ở đây.\n' +
            f'» {intro_channel.mention} giới thiệu bản thân.\n' +
            f'» Qua {bot_channel.mention} để thêm Role cho mình, mở thêm các kênh chat và kênh tin tức cho game!\n\n' +
            f'Nhập lệnh `{bot.command_prefix}help` để được hỗ trợ thêm nhé.')

        await bot.send_message(welcome_channel, message)

db = util.initialize_db()
event_db = db.worksheet('match_word_event')


async def match_word_event(message, channel, sleep=5):

    timestamps = event_db.acell('D2').value
    last_uid = event_db.acell('A2').value
    last_word = event_db.acell('C2').value
    non_word_re = re.compile('\W')
    word = message.content.lstrip('>').strip().lower()
    word = non_word_re.sub('', word)
    posted_words = event_db.col_values(3)

    # returns None, None if unable to parse time
    passed, time_wait = util.check_delay(timestamps, 10)

    if message.author.id == last_uid:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, vui lòng đợi người khác nối chữ của mình nhé!')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif passed is False:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, vui lòng đợi thêm {time_wait} giây nữa.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif last_word and word[0] != last_word[-1]:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, vui lòng chọn chữ bắt đầu với ký tự `{last_word[-1].upper()}`.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif word in posted_words:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, đã có người sử dụng chữ này. Vui lòng chọn chữ khác.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)

    # 'passed' is True, or 'passed' is None, or passed the above tests
    else:
        now = datetime.now()
        event_db.insert_row([message.author.id, message.author.name, word, str(now)], index=2)
        success_note = await bot.send_message(
            channel,
            f'{message.author.mention}, chữ hợp lệ. Xin cảm ơn đã tham gia!')
        await asyncio.sleep(sleep)
        await bot.delete_message(success_note)


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
        role_request_channel = server.get_channel('453930352365273099')
        match_word_channel = util.get_channel(server, id='458260628876951552')

        if message.channel == role_request_channel and message.content.startswith(bot.command_prefix):
            await bot.delete_message(message)

        # proc event
        # elif message.channel == match_word_channel and message.content.startswith('>'):

        #     await match_word_event(message, match_word_channel)

        else:
            await bot.process_commands(message)

twitter_tasks = tasks.Twitter(bot, util)
facebook_tasks = tasks.Facebook(bot, util)

bot.loop.create_task(webspiders.WebSpider(bot, util).parse())
bot.loop.create_task(twitter_tasks.fetch_maplem_latest_tweet())
bot.loop.create_task(twitter_tasks.fetch_maple_latest_tweet())


# if config.DEBUG:
# bot.loop.create_task(facebook_tasks.fb())
# bot.loop.create_task(webspiders.WebSpider(bot, util).parse())

bot.run(config.BOT_TOKEN)
