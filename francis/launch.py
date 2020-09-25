import traceback

import config
from francis import bot

if config.DEBUG is True:
    prefix = '.'
else:
    prefix = '!'

francis = bot.CustomBot(
    command_prefix=prefix,
    description='Francis - Orchid\'s slave',
    max_messages=10000,
)
# remove the 'help' command
francis.remove_command('help')

# initialize francis's utility functions
# util = Utility(francis)

initial_extensions = [

    'francis.cogs.admin',
    'francis.cogs.dailies',
    'francis.cogs.help',
    # 'francis.cogs.investigate',
    'francis.cogs.link',
    'francis.cogs.logger',
    'francis.cogs.mudae',
    'francis.cogs.owner',
    # 'francis.cogs.profile',
    'francis.cogs.requirement',
    'francis.cogs.role',
    # 'francis.cogs.old.gacha',
    # 'francis.cogs.old.stat_check',

]

if not config.DEBUG:
    initial_extensions += [
        # 'francis.tasks.tiki',
        'francis.tasks.socials',
        'francis.tasks.crawlers'
    ]
else:
    initial_extensions += [
        'francis.tasks.socials',
        'francis.tasks.crawlers'
    ]

for extension in initial_extensions:
    try:
        francis.load_extension(extension)
    except Exception as e:
        traceback.print_exc()

francis.run(config.FRANCIS_TOKEN)
