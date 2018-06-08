import discord
from var import *


class Utility:
    def __init__(self, bot):
        self.bot = bot

    async def say_as_embed(self, message=None, title=None, embed=None, color='info'):
        """Make the bot say as an Embed.
        Passing an 'embed' will send it instead.
        Shortcut for color kwarg: 'info' (default), 'warning', 'error', 'success'
        """

        if color == 'info':
            color = discord.Color.teal()
        elif color == 'warning':
            color = discord.Color.gold()
        elif color == 'error':
            color = discord.Color.red()
        elif color == 'success':
            color = discord.Color.green()

        if embed is None:
            embed = discord.Embed(
                title=title,
                description=message,
                colour=color)
            await self.bot.say(embed=embed)
        else:
            await self.bot.say(embed=embed)

    async def send_message_as_embed(self, channel, message=None, title=None, color='info'):
        """Send a message to a specified channel as an Embed.
        Passing an 'embed' will send it instead, and ignore things in 'message' kwarg.
        Shortcut for color kwarg: 'info' (default), 'warning', 'error', 'success'
        """

        if color == 'info':
            color = discord.Color.teal()
        elif color == 'warning':
            color = discord.Color.gold()
        elif color == 'error':
            color = discord.Color.red()
        elif color == 'success':
            color = discord.Color.green()

        if embed is None:
            embed = discord.Embed(
                title=title,
                description=message,
                colour=color)
            await self.bot.send_message(channel, embed=embed)
        else:
            await self.bot.send_message(channel, embed=embed)

    async def process_role(self, role):
        """Process the role given by the user.
        Return None if no roles detected"""

        # strip the leading @ in case someone fucks up
        role = role.lstrip('@')

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
