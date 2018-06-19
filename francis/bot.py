import discord
from discord.ext import commands


class FrancisBot(commands.Bot):

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
            await self.say(embed=embed)
        else:
            await self.say(embed=embed)

    async def send_message_as_embed(self, channel, message=None, title=None, embed=None, color='info'):
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
            await self.send_message(channel, embed=embed)
        else:
            await self.send_message(channel, embed=embed)
