import discord
from discord.ext import commands

from var import *


class Role:
    """A cog for role management commands"""

    def __init__(self, bot, util):
        self.bot = bot
        self.util = util

    @commands.command(pass_context=True)
    async def role(self, context, role=None):
        """Set Role theo yêu cầu"""
        message = context.message
        author = message.author
        prefix = self.bot.command_prefix

        if role is None:

            embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Color.teal())
            embed.add_field(
                name=f'Cú pháp: `{prefix}role tên_role`',
                value=f'Dùng lệnh này để yêu cầu bot thêm Role cho bạn. Nhập lệnh `{prefix}list` để xem danh sách Role.')
            await self.util.say_as_embed(embed=embed)

        else:

            # process the role to match server's role names
            # returns None if no roles detected
            role = await self.util.process_role(role)

            if role is not None:

                r = discord.utils.get(message.server.roles, name=role)

                if r in author.roles:
                    await self.util.say_as_embed(message=f'{author.mention} có role này rồi nhé.')

                else:
                    await self.bot.add_roles(author, r)
                    await self.util.say_as_embed(
                        message=f'{author.mention} đã được set role {r.mention}.',
                        color=r.color)
            else:
                await self.util.say_as_embed(
                    message=f'{author.mention}, role này không tồn tại hoặc không tự xử được nha. Gõ `{prefix}list` để xem các Role.',
                    color='error')

    @commands.command(pass_context=True)
    async def rrole(self, context, role=None, role_type=None):
        """Xóa Role theo yêu cầu
        - Xóa từng role: !rrole tên_role
        - Xóa nhiều role: !rrole all loại_role
        (loại_role là colors hoặc channels hoặc all)

        """
        message = context.message
        author = message.author
        prefix = self.bot.command_prefix

        # empty requested role, show help
        if role is None:

            embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Color.teal())
            embed.add_field(
                name=f'Cú pháp xóa 1 Role: `{prefix}rrole tên_role`',
                value=f'Nhập lệnh `{prefix}list` để xem danh sách Role có thể xóa.\n'
                'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.')
            embed.add_field(
                name=f'Cú pháp xóa nhiều Role: `{prefix}rrole all loại_role`',
                value=f'`loại_role` có thể là `colors`, `channels`, hoặc `all`\n'
                '» `colors` - Xóa tất cả Role màu sắc bạn đang có.\n'
                '» `channels` - Xóa tất cả Role kênh bạn đang có.\n'
                '» `all` - Xóa tất cả mọi Role bạn đang có.\n'
                f'Nhập lệnh `{prefix}list` để xem danh sách Role có thể xóa.')
            await self.util.say_as_embed(embed=embed)

        # requested role input detected
        else:
            # process the role to match server's role names
            # returns None if no roles detected
            role = await self.util.process_role(role)

            # proc role is 'all' trying to remove multiple roles
            if role == 'all':
                # check invalid role_type or None
                if role_type is None or role_type not in ['colors', 'colours', 'channels', 'all']:

                    embed = discord.Embed(
                        title=None,
                        description=None,
                        color=discord.Color.teal())
                    embed.add_field(
                        name=f'Cú pháp xóa nhiều Role: `{prefix}rrole all loại_role`',
                        value=f'`loại_role` có thể là `colors`, `channels`, hoặc `all`\n'
                        '» `colors` - Xóa tất cả Role màu sắc bạn đang có.\n'
                        '» `channels` - Xóa tất cả Role kênh bạn đang có.\n'
                        '» `all` - Xóa tất cả mọi Role bạn đang có.\n'
                        f'Nhập lệnh `{prefix}list` để xem danh sách Role có thể xóa.')
                    await self.util.say_as_embed(embed=embed)

                # remove roles by valid provided role_type
                else:

                    # initiate stuff to use
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

                    # remove roles if there are any
                    if to_rmv_roles['roles']:
                        await self.bot.remove_roles(author, *to_rmv_roles['roles'])
                        mention_roles = ", ".join(to_rmv_roles['role_mentions'])
                        await self.util.say_as_embed(
                            message=f'{author.mention}, role {mention_roles} đã được xóa thành công.',
                            color='success')
                    else:
                        await self.util.say_as_embed(
                            message=f'{author.mention}, không có Role nào thuộc `loại_role` này.',
                            color='error')

            elif role is not None:

                r = discord.utils.get(message.server.roles, name=role)

                if r not in author.roles:
                    await self.util.say_as_embed(
                        message=f'{author.mention} không có role này.\n'
                        'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.',
                        color='error')

                else:
                    await self.bot.remove_roles(author, r)
                    await self.util.say_as_embed(
                        message=f'{author.mention}, role {r.mention} đã được xóa thành công.',
                        color='success')

            else:
                await self.util.say_as_embed(
                    message=f'{author.mention}, role này không tồn tại hoặc không tự xử được nha. Gõ `{prefix}list` để xem các Role.',
                    color='error')

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
