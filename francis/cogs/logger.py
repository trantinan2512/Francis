from datetime import datetime
from discord.ext import commands
import discord
import io
# import asyncio
# import operator
from pprint import pprint
from django.conf import settings


class LoggerCog(commands.Cog):
    """Logger stuff"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.content == after.content:
            return

        embed = discord.Embed(
            title='Message edited',
            description=
            f'• Author: {before.author.mention} (ID: `{before.author.id}`)\n'
            f'• Jump URL: [Click here]({before.jump_url})',
            color=discord.Color.dark_green(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name='Before',
            value=str(before.content) or 'N/A',
            inline=False
        )

        embed.add_field(
            name='After',
            value=str(after.content) or 'N/A',
            inline=False
        )

        channel = self.bot.get_channel(529170877724753948)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        embed = discord.Embed(
            title='Message deleted',
            description=
            f'• Channel: <#{payload.channel_id}>\n',
            color=discord.Color.dark_green(),
            timestamp=datetime.utcnow()
        )

        channel = self.bot.get_channel(529170877724753948)

        if payload.cached_message:
            message = payload.cached_message
            embed.description += f'• Author: {message.author.mention}\n'
            embed.add_field(
                name='Content',
                value=message.content or 'N/A',
                inline=False
            )

            if message.attachments:
                files = []
                for att in message.attachments:
                    # print(settings.BASE_DIR, att.filename)
                    await att.save(fp=f'{settings.BASE_DIR}\\attachments\\{att.filename}', use_cached=True)
                    file = discord.File(fp=f'{settings.BASE_DIR}\\attachments\\{att.filename}')
                    files.append(file)

                if files:
                    msg = await channel.send(files=files)

                    attachment_txt = f'• Jump URL: [Click here]({msg.jump_url})\n'
                    attachment_txt += '• URLs: '
                    attachment_txt += ' | '.join([f'[Attachment_{i}]({a.url})' for i, a in enumerate(msg.attachments, start=1)])
                    embed.add_field(
                        name='Attachments',
                        value=attachment_txt or 'N/A'
                    )
        else:
            embed.description += f'• Status: *Not a cached message*'

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(LoggerCog(bot))
