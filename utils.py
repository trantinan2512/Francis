import discord
from var import *


class Utility:
    def __init__(self, bot):
        self.bot = bot

    async def say_as_embed(self, message=None, title=None, embed=None, color=discord.Color.teal()):
        """Make the bot say as an Embed.
        Passing an 'embed' will send it instead.
        """
        if embed is None:
            embed = discord.Embed(
                title=title,
                description=message,
                colour=color)
            await self.bot.say(embed=embed)
        else:
            await self.bot.say(embed=embed)

    async def send_message_as_embed(self, channel, message, title=None, color=discord.Color.teal()):
        """Make the bot say as an Embed."""
        embed = discord.Embed(
            title=title,
            description=message,
            colour=color)
        await self.bot.send_message(channel, embed=embed)

    async def process_role(self, role):
        """Process the role given by the user"""
        if role in AUTOASIGN_ROLES:
            return role
        elif role.capitalize() in AUTOASIGN_ROLES:
            return role.capitalize()
        elif role.upper() in AUTOASIGN_ROLES:
            return role.upper()
        elif role == 'all':
            return 'all'
        else:
            return None
