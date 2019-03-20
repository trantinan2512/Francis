import discord
import traceback
from francis import bot
from francis.tasks import socials, webspiders, schedules
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
    'francis.cogs.investigate',
    'francis.cogs.link',
    'francis.cogs.profile',
    'francis.cogs.requirement',
    'francis.cogs.role',
    'francis.cogs.old.gacha',
    'francis.cogs.old.stat_check'
)
for extension in initial_extensions:
    try:
        francis.load_extension(extension)
    except Exception as e:
        traceback.print_exc()


# EVENTS

@francis.event
async def on_ready():
    print('------')
    print(f'Logged in as: {francis.user.name} (ID: {francis.user.id})')
    print('------')

    if not config.DEBUG:
        await francis.change_presence(activity=discord.Game(name=f'{francis.command_prefix}help'))
    else:
        await francis.change_presence(activity=discord.Game(name=f'{francis.command_prefix}help'))


if not config.DEBUG:
    francis.loop.create_task(webspiders.GMSSiteSpider(francis).parse())
    francis.loop.create_task(webspiders.GMS2SiteSpider(francis).parse())
    francis.loop.create_task(webspiders.GMSMSiteSpider(francis).parse())
    francis.loop.create_task(socials.Twitter(francis).fetch_maple_latest_tweet())
    francis.loop.create_task(socials.Twitter(francis).fetch_maple2_latest_tweet())
    francis.loop.create_task(socials.Twitter(francis).fetch_maplem_latest_tweet())
    francis.loop.create_task(schedules.Scheduler(francis).check_gms_schedule())
    francis.loop.create_task(schedules.Scheduler(francis).check_gmsm_schedule())
    francis.loop.create_task(schedules.Scheduler(francis).check_dawn_schedule())
else:
    # francis.loop.create_task(webspiders.GMSSiteSpider(francis).parse())
    # francis.loop.create_task(webspiders.GMS2SiteSpider(francis).parse())
    # francis.loop.create_task(webspiders.GMSMSiteSpider(francis).parse())
    # francis.loop.create_task(socials.Twitter(francis).fetch_maple_latest_tweet())
    # francis.loop.create_task(socials.Twitter(francis).fetch_maple2_latest_tweet())
    # francis.loop.create_task(socials.Twitter(francis).fetch_maplem_latest_tweet())
    # francis.loop.create_task(schedules.Scheduler(francis).check_gms_schedule())
    # francis.loop.create_task(schedules.Scheduler(francis).check_gmsm_schedule())
    # francis.loop.create_task(schedules.Scheduler(francis).check_dawn_schedule())
    pass

francis.run(config.FRANCIS_TOKEN)
