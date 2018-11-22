import discord
from francis import bot
from francis.cogs import tasks, webspiders, scheduler
import config

if config.DEBUG is True:
    prefix = '.'
else:
    prefix = '!'


francis = bot.CustomBot(command_prefix=prefix, description='Francis - Orchid\'s slave')
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

    if not config.DEBUG:
        await francis.change_presence(game=discord.Game(name=f'{francis.command_prefix}help << hàng thật'))
    else:
        await francis.change_presence(game=discord.Game(name=f'{francis.command_prefix}help << hàng thật'))


@francis.event
async def on_member_join(member):
    """Says when a member joined."""
    welcome_channel = francis.get_channel(453886339570597890)
    rules_channel = francis.get_channel(453566033190584321)
    intro_channel = francis.get_channel(455025500071526401)
    francis_channel = francis.get_channel(454310191962390529)
    role_channel = francis.get_channel(472965546485481473)

    message = (
        f'Chào mừng **{member.mention}** đã đến với **{member.server.name}**!\n\n' +
        f'Dưới đây là hướng dẫn tương tác với group nhé!\n' +
        f'» Đọc {rules_channel.mention} ở đây.\n' +
        f'» {intro_channel.mention} giới thiệu bản thân.\n' +
        f'» Qua kênh {role_channel.mention} để nhận danh hiệu ứng với game mình đang chơi!\n\n' +
        f'Nhập lệnh `{francis.command_prefix}help` ở kênh {francis_channel.mention} để được hỗ trợ thêm nhé.')

    await welcome_channel.send(message)


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

francis.run(config.FRANCIS_TOKEN)
