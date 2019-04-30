from discord.ext import commands
import discord
# import asyncio
# import operator
# from pprint import pprint
from utils.user import get_user_obj


class ProfileCommands(commands.Cog):
    """Profile related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eprofile')
    async def _check_event_profile(self, context):

        # prefix = self.bot.command_prefix
        user = get_user_obj(context.author)
        hint_count = len(user.investigation_info.discovered_hints)
        await context.say_as_embed(
            title=f'[{user.discord_name}] Event Profile',
            description=''
            f'**2018 Year-End Event**\n'
            f'• Discovered Hints Counter: **{hint_count}**'
        )


def setup(bot):
    bot.add_cog(ProfileCommands(bot))
