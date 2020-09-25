import discord
from discord.ext import commands

import config


class GenshinRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        ponpon_guild = self.bot.get_guild(config.PON_SERVER_ID)
        if not ponpon_guild:
            return

        dawn_rfr = {}
        for emoji_id, role_id in zip(config.PONPON_ROLE_REACT_EMOJI_IDS, config.PONPON_ROLE_REACT_ROLE_IDS):
            dawn_rfr.update({int(emoji_id): ponpon_guild.get_role(int(role_id))})

        member = ponpon_guild.get_member(payload.user_id)
        if not member:
            return

        if payload.emoji.id in dawn_rfr:

            if payload.channel_id != 759034043810578433:
                return

            channel = ponpon_guild.get_channel(payload.channel_id)

            character_role_count = 0
            for member_role in member.roles:
                if member_role.id in config.PONPON_ROLE_REACT_ROLE_IDS:
                    character_role_count += 1
                    if character_role_count >= 4:
                        await channel.send(embed=discord.Embed(
                            title='',
                            description=
                            f'{member.mention}, you can only have up to 4 character roles.\n'
                            f'Remove other reactions first, then try again.',
                            color=discord.Color.dark_red()),
                            delete_after=5
                        )
                        message = await channel.fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji, member)
                        return

            await member.add_roles(dawn_rfr[payload.emoji.id])

            embed = discord.Embed(
                title='',
                description=
                f'{member.mention} obtained '
                f'{dawn_rfr[payload.emoji.id].mention} role.',
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed, delete_after=5)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        ponpon_guild = self.bot.get_guild(config.PON_SERVER_ID)
        if not ponpon_guild:
            return

        dawn_rfr = {}
        for emoji_id, role_id in zip(config.PONPON_ROLE_REACT_EMOJI_IDS, config.PONPON_ROLE_REACT_ROLE_IDS):
            dawn_rfr.update({int(emoji_id): ponpon_guild.get_role(int(role_id))})

        member = ponpon_guild.get_member(payload.user_id)
        if not member:
            return

        if payload.emoji.id in dawn_rfr:
            if payload.channel_id != 759034043810578433:
                return

            member = ponpon_guild.get_member(payload.user_id)
            role_remove = dawn_rfr[payload.emoji.id]
            # do nothing if there's nothing to remove
            if role_remove.id not in [member_role.id for member_role in member.roles]:
                return

            await member.remove_roles(role_remove)

            channel = ponpon_guild.get_channel(payload.channel_id)
            embed = discord.Embed(
                title='',
                description=
                f'{dawn_rfr[payload.emoji.id].mention} role '
                f'has been removed from {member.mention}.',
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed, delete_after=5)


def setup(bot):
    bot.add_cog(GenshinRole(bot))
