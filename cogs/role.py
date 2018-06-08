import discord
from discord.ext import commands

from var import *


class Role:
    """A cog for role management commands"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

    @commands.command(pass_context=True)
    async def role(self, context, role: str):
        """Set Role theo yêu cầu"""
        message = context.message
        author = message.author

        role = await self.util.process_role(role)

        if role is not None:

            r = discord.utils.get(message.server.roles, name=role)

            if r is not None:

                if r in author.roles:
                    await self.bot.say(f'{author.mention} có role này rồi nhé.')

                else:
                    await self.bot.add_roles(author, r)
                    await self.util.say_as_embed(
                        message=f'{author.mention} đã được set role {r.mention}.',
                        color=r.color)

            else:
                await self.bot.say(f'{author.mention}, role này không tồn tại.')
        else:
            await self.bot.say(f'{author.mention}, role này không tồn tại hoặc không tự xử được nha.')

    @commands.command(pass_context=True)
    async def rrole(self, context, role: str, role_type=None):
        """Xóa Role theo yêu cầu
        - Xóa từng role: !rrole tên_role
        - Xóa nhiều role: !rrole all loại_role
        (loại_role là colors hoặc channels hoặc all)

        """
        message = context.message
        author = message.author

        role = await self.util.process_role(role)

        if role == 'all':
            to_rmv_roles = {
                'roles': [],
                'role_mentions': []
            }

            for r in author.roles:
                if role_type == 'colors' or role_type == 'colours':
                    if r.name in AUTOASIGN_COLOR_ROLES:
                        to_rmv_roles['roles'].append(r)
                        to_rmv_roles['role_mentions'].append(r.mention)
                elif role_type == 'channels':
                    if r.name in AUTOASIGN_CHANNEL_ROLES:
                        to_rmv_roles['roles'].append(r)
                        to_rmv_roles['role_mentions'].append(r.mention)
                elif role_type == 'all':
                    if r.name in AUTOASIGN_ROLES:
                        to_rmv_roles['roles'].append(r)
                        to_rmv_roles['role_mentions'].append(r.mention)

            if to_rmv_roles['roles']:
                await self.bot.remove_roles(author, *to_rmv_roles['roles'])
                mention_roles = ", ".join(to_rmv_roles['role_mentions'])
                await self.util.say_as_embed(
                    message=f'{author.mention}, role {mention_roles} đã được xóa thành công.')
            else:
                await self.util.say_as_embed(
                    message=f'{author.mention}, vui lòng chỉ định đúng nhóm role muốn xóa (colors/channels/all).',
                    color=discord.Color.dark_red())

        elif role is not None:

            r = discord.utils.get(message.server.roles, name=role)

            if r is not None:

                if r not in author.roles:
                    await self.bot.say(f'{author.mention} không có role này.')

                else:
                    await self.bot.remove_roles(author, r)
                    await self.util.say_as_embed(
                        message=f'{author.mention}, role {r.mention} đã được xóa thành công.',
                        color=r.color)

            else:
                await self.bot.say(f'{author.mention}, role này không tồn tại.')
        else:
            await self.bot.say(f'{author.mention}, role này không tồn tại hoặc không tự xử được nha.')

    @commands.command(pass_context=True)
    async def list(self, context):
        """Xem danh sách Role có thể tự thêm/xóa"""
        message = context.message
        server = message.server

        embed = discord.Embed(
            title='Danh sách Role có thể tự thêm/xóa',
            description=None,
            colour=discord.Color.teal())

        ch_roles = []
        co_roles = []

        for role_name in AUTOASIGN_CHANNEL_ROLES:
            r = discord.utils.get(server.roles, name=role_name)
            if r is not None:
                ch_roles.append(r.mention)

        for role_name in AUTOASIGN_COLOR_ROLES:
            r = discord.utils.get(server.roles, name=role_name)
            if r is not None:
                co_roles.append(r.mention)

        embed.add_field(name='Channel Roles', value='\n'.join(ch_roles))
        embed.add_field(name='Color Roles', value='\n'.join(co_roles))
        await self.bot.say(embed=embed)
