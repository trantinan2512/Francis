import discord
# import json
import asyncio
# from datetime import datetime
# import re
# from discord.ext import commands
from discord.errors import HTTPException
# from pypresence import Presence
# import time
# from datetime import datetime

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
    'francis.cogs.gacha',
    'francis.cogs.stat_check'
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

    # print('Running PyPresence...')
    # client_id = "453579291897233409"  # Enter your Application ID here.
    # RPC = Presence(client_id=client_id)
    # RPC.connect()

    # now = datetime.now()
    # now_unix = time.mktime(now.timetuple())
    # now_unix = int(now_unix)
    # # Make sure you are using the same name that you used when uploading the image
    # RPC.update(
    #     large_image="orchid_wink", large_text="Best Girl! *wink wink*",
    #     small_image="rrain", small_text="SAO waifu",
    #     details="Battlefield: Bed", state="This is for Nijika - Rain :HAAHa:",
    #     start=now_unix)
    # print('PyPresence running!')

    if not config.DEBUG:
        await francis.change_presence(game=discord.Game(name=f'{francis.command_prefix}help << hàng thật'))
    else:
        await francis.change_presence(game=discord.Game(name=f'{francis.command_prefix}help << hàng thật'))

    open_channel = francis.get_channel('472965546485481473')
    channel_msg = await francis.get_message(open_channel, '472966572340674560')
    notify_msg = await francis.get_message(open_channel, '472967231781863427')

    if channel_msg not in francis.messages:
        francis.messages.append(channel_msg)
    if notify_msg not in francis.messages:
        francis.messages.append(notify_msg)


@francis.event
async def on_member_join(member):
    """Says when a member joined."""

    if not config.DEBUG:

        server = member.server
        welcome_channel = server.get_channel('453886339570597890')
        rules_channel = server.get_channel('453566033190584321')
        intro_channel = server.get_channel('455025500071526401')
        francis_channel = server.get_channel('454310191962390529')
        open_channel = francis.get_channel('472965546485481473')

        message = (
            f'Chào mừng **{member.mention}** đã đến với **{member.server.name}**!\n\n' +
            f'Dưới đây là hướng dẫn tương tác với group nhé!\n' +
            f'» Đọc {rules_channel.mention} ở đây.\n' +
            f'» {intro_channel.mention} giới thiệu bản thân.\n' +
            f'» Qua kênh {open_channel.mention} để mở thêm các kênh chat và kênh tin tức cho game!\n\n' +
            f'Nhập lệnh `{francis.command_prefix}help` ở kênh {francis_channel.mention} để được hỗ trợ thêm nhé.')

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
        open_channel = francis.get_channel('472965546485481473')

        # delete messages that start with the bot's command prefix to avoid spamming in the channel
        if message.channel == role_request_channel and message.content.startswith(francis.command_prefix):
            await francis.delete_message(message)
        # delete messages that are an embed (aka bot) in the open_channel (self-asigned roles)
        elif message.channel == open_channel and message.embeds:
            await asyncio.sleep(5)
            await francis.delete_message(message)

        else:
            await francis.process_commands(message)


@francis.event
async def on_reaction_add(reaction, user):
    open_channel = francis.get_channel('472965546485481473')
    if reaction.message.channel == open_channel:

        gms_role = discord.utils.get(reaction.message.server.roles, name='GMS')
        gmsm_role = discord.utils.get(reaction.message.server.roles, name='GMSM')
        gms_notify = discord.utils.get(reaction.message.server.roles, name='Notify GMS')
        gmsm_notify = discord.utils.get(reaction.message.server.roles, name='Notify GMSM')
        if reaction.message.id == '472966572340674560':
            if reaction.emoji == '📱':
                await francis.add_roles(user, gmsm_role)
                await francis.send_message_as_embed(
                    open_channel,
                    f'{user.mention} đã có thể xem các kênh liên quan đến {gmsm_role.mention}')

            elif reaction.emoji == '🖥':
                await francis.add_roles(user, gms_role)
                await francis.send_message_as_embed(
                    open_channel,
                    f'{user.mention} đã có thể xem các kênh liên quan đến {gms_role.mention}')

        elif reaction.message.id == '472967231781863427':
            if reaction.emoji == '📱':
                await francis.add_roles(user, gmsm_notify)
                await francis.send_message_as_embed(open_channel, f'{user.mention} sẽ nhận được thông báo khi ping {gmsm_notify.mention}')

            elif reaction.emoji == '🖥':
                await francis.add_roles(user, gms_notify)
                await francis.send_message_as_embed(open_channel, f'{user.mention} sẽ nhận được thông báo khi ping {gms_notify.mention}')


@francis.event
async def on_reaction_remove(reaction, user):
    open_channel = francis.get_channel('472965546485481473')
    if reaction.message.channel == open_channel:

        gms_role = discord.utils.get(reaction.message.server.roles, name='GMS')
        gmsm_role = discord.utils.get(reaction.message.server.roles, name='GMSM')
        gms_notify = discord.utils.get(reaction.message.server.roles, name='Notify GMS')
        gmsm_notify = discord.utils.get(reaction.message.server.roles, name='Notify GMSM')
        if reaction.message.id == '472966572340674560':
            if reaction.emoji == '📱':
                await francis.remove_roles(user, gmsm_role)
                await francis.send_message_as_embed(
                    open_channel,
                    f'{user.mention} không còn xem được các kênh liên quan đến {gmsm_role.mention} nữa.')

            elif reaction.emoji == '🖥':
                await francis.remove_roles(user, gms_role)
                await francis.send_message_as_embed(
                    open_channel,
                    f'{user.mention} không còn xem được các kênh liên quan đến {gms_role.mention} nữa.')

        elif reaction.message.id == '472967231781863427':
            if reaction.emoji == '📱':
                await francis.remove_roles(user, gmsm_notify)
                await francis.send_message_as_embed(
                    open_channel,
                    f'{user.mention} sẽ không nhận thông báo khi ping {gmsm_notify.mention} nữa.')

            elif reaction.emoji == '🖥':
                await francis.remove_roles(user, gms_notify)
                await francis.send_message_as_embed(
                    open_channel,
                    f'{user.mention} sẽ không nhận thông báo khi ping {gms_notify.mention} nữa.')


if not config.DEBUG:
    francis.loop.create_task(webspiders.GMSSiteSpider(francis).parse())
    francis.loop.create_task(webspiders.GMS2SiteSpider(francis).parse())
    francis.loop.create_task(webspiders.GMSMSiteSpider(francis).parse())
    francis.loop.create_task(tasks.Twitter(francis).fetch_maple_latest_tweet())
    francis.loop.create_task(tasks.Twitter(francis).fetch_maple2_latest_tweet())
    francis.loop.create_task(tasks.Twitter(francis).fetch_maplem_latest_tweet())
    francis.loop.create_task(scheduler.Scheduler(francis).check_gms_schedule())
    francis.loop.create_task(scheduler.Scheduler(francis).check_gmsm_schedule())
    francis.loop.create_task(scheduler.Scheduler(francis).check_dawn_schedule())

# if config.DEBUG:
#     francis.loop.create_task(tasks.Twitter(francis).fetch_maple2_latest_tweet())

francis.run(config.FRANCIS_TOKEN)
