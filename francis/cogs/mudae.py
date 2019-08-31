import discord
from discord.ext import commands
from francis.utils.role import process_role
from francis.converters import CustomRoleConverter
from utils.user import get_user_obj
import config
from datetime import datetime


class Mudae(commands.Cog):
    """A cog for role management commands"""

    def __init__(self, bot):
        self.bot = bot
        self.mudae_channel_id = 617360428414140426 if config.DEBUG else 615526988270010428
        self.mudae_user_id = 545293375654592512
        self.check_channel_id = 617360428414140426

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.guild_id != config.DAWN_SERVER_ID:
            return

        if payload.channel_id != self.mudae_channel_id:
            return

        # if payload.user_id == self.mudae_user_id:
        #     return

        channel = self.bot.get_channel(self.mudae_channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.HTTPException:
            return

        check_channel = self.bot.get_channel(self.check_channel_id)
        if not check_channel:
            return

        embed = discord.Embed(
            title='Waifu might be claimed',
            color=discord.Color.dark_blue()
        )
        embed.set_footer(text=f'{payload.message_id}')

        msg = await check_channel.send(embed=embed)
        embed.description = (
            f'[The message](https://discordapp.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id}) '
            f'has been reacted by <@{payload.user_id}> likely to claim a waifu in **{msg.created_at - message.created_at}** secs.\n'
            f'Emoji reacted: {payload.emoji}'
        )
        await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(Mudae(bot))
