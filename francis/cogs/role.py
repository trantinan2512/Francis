import discord
from discord.ext import commands
from francis.utils.role import process_role
import config


class Role:
    """A cog for role management commands"""

    def __init__(self, bot):
        self.bot = bot

    def good_for_role_assign(ctx):
        author = ctx.author
        server = ctx.guild

        # Dawn member check
        if server.id == config.DAWN_SERVER_ID:
            dawn_role = discord.utils.get(author.roles, id=364967220193001472)
            collector_role = discord.utils.get(author.roles, id=544542640838934528)
            if dawn_role or collector_role:
                return True
            else:
                return False
        else:
            return True

    @commands.command(aliases=['role', 'iam'])
    @commands.check(good_for_role_assign)
    async def _role(self, context, *, role=None):
        """Set Role theo yêu cầu"""

        message = context.message
        author = message.author
        server = message.guild
        prefix = self.bot.command_prefix

        if server.id == config.MSVN_SERVER_ID:
            field_1_name = f'Cú pháp: `{prefix}role tên_role`'
            field_1_value = f'Dùng lệnh này để yêu cầu bot thêm Role cho bạn. Nhập lệnh `{prefix}list` để xem danh sách Role.'
            role_exists_msg = f'{author.mention} có role này rồi nhé.'
            wrong_role_name_provided_msg = f'{author.mention}, role này không tồn tại hoặc không tự xử được nha. '
            wrong_role_name_provided_msg += f'Gõ `{prefix}list` để xem các Role.'
        elif server.id == config.DAWN_SERVER_ID:
            dawn_role = discord.utils.get(server.roles, id=364967220193001472)
            collector_role = discord.utils.get(server.roles, id=544542640838934528)

            field_1_name = f'Format: `{prefix}role role_name`'
            field_1_value = f'Use this command to auto-asign a Role. Type `{prefix}list` to see a full list of available roles.\n'
            field_1_value += f'**This command is available for {dawn_role.mention} and {collector_role.mention} only**.'
            role_exists_msg = f'{author.mention}, you already have this role.'
            wrong_role_name_provided_msg = f'{author.mention}, this role does not exist, or not auto-asignable. '
            wrong_role_name_provided_msg += f'Type `{prefix}list` to see a full list of available roles.'

        if role is None:

            embed = discord.Embed(
                title=field_1_name,
                description=field_1_value,
                color=discord.Color.teal())
            await context.say_as_embed(embed=embed)

        else:

            # process the role to match server's role names
            # returns None if no roles detected
            role = process_role(role)

            if type(role) != tuple and role is not None:

                r = discord.utils.get(message.guild.roles, name=role)
                if server.id == config.MSVN_SERVER_ID:
                    role_set_msg = f'{author.mention} đã được set role {r.mention}.'
                elif server.id == config.DAWN_SERVER_ID:
                    role_set_msg = f'{author.mention}, you now have {r.mention} role.'

                if r in author.roles:
                    await context.say_as_embed(message=role_exists_msg)

                else:
                    await author.add_roles(r)
                    await context.say_as_embed(
                        message=role_set_msg,
                        color=r.color)
            else:
                await context.say_as_embed(
                    message=wrong_role_name_provided_msg,
                    color='error')

    @commands.command(aliases=['rrole', 'iamn'])
    @commands.check(good_for_role_assign)
    async def _rrole(self, context, *, role=None):
        """Xóa Role theo yêu cầu
        - Xóa từng role: !rrole tên_role
        - Xóa nhiều role: !rrole all loại_role
        (loại_role là colors hoặc channels hoặc all)
        """
        message = context.message
        author = message.author
        server = message.guild
        prefix = self.bot.command_prefix

        if server.id == config.MSVN_SERVER_ID:
            field_1_name = f'Cú pháp xóa 1 Role: `{prefix}rrole tên_role`'
            field_1_value = f'Nhập lệnh `{prefix}list` để xem danh sách Role có thể xóa.\n'
            field_1_value += 'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.'

            field_2_name = f'Cú pháp xóa nhiều Role: `{prefix}rrole all loại_role`'
            field_2_value = f'`loại_role` có thể là `colors`, `channels`, `jobs`, hoặc `all`\n'
            field_2_value += '» `colors` - Xóa tất cả Role màu sắc bạn đang có.\n'
            field_2_value += '» `channels` - Xóa tất cả Role kênh bạn đang có.\n'
            field_2_value += '» `jobs` - Xóa tất cả Role Job bạn đang có.\n'
            field_2_value += '» `notify` - Xóa tất cả Role Notification bạn đang có.\n'
            field_2_value += '» `all` - Xóa tất cả mọi Role bạn đang có.\n'
            field_2_value += f'Nhập lệnh `{prefix}list` để xem danh sách Role có thể xóa.'

            no_role_found_msg = f'{author.mention} không có role này.\n'
            no_role_found_msg += 'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.'

            wrong_role_name_provided_msg = f'{author.mention}, role này không tồn tại hoặc không tự xử được nha. '
            wrong_role_name_provided_msg += f'Gõ `{prefix}list` để xem các Role.'

        elif server.id == config.DAWN_SERVER_ID:
            dawn_role = discord.utils.get(server.roles, id=364967220193001472)
            collector_role = discord.utils.get(server.roles, id=544542640838934528)

            field_1_name = f'Format: `{prefix}rrole role_name`'
            field_1_value = f'Use this command to remove an auto-asigned Role.\n'
            field_1_value += f'**This command is available for {dawn_role.mention} and {collector_role.mention} only**.'

            field_2_name = f'Remove multiple Roles: `{prefix}rrole all role_type`'
            field_2_value = f'`role_type` can be `colors`\n'
            field_2_value += '» `colors` - Remove all **Color Roles** you have.\n'
            field_2_value += f'Type `{prefix}list` to see a full list of available roles.'

            wrong_role_name_provided_msg = f'{author.mention}, this role does not exist, or not auto-asignable. '
            wrong_role_name_provided_msg += f'Type `{prefix}list` to see a full list of available roles.'

        # empty requested role, show help
        if role is None:

            embed = discord.Embed(
                title=None,
                description=None,
                color=discord.Color.teal())
            embed.add_field(
                name=field_1_name,
                value=field_1_value)
            embed.add_field(
                name=field_2_name,
                value=field_2_value)
            await context.say_as_embed(embed=embed)

        # requested role input detected
        else:
            # process the role to match server's role names
            # returns None if no roles detected
            r = process_role(role)
            if type(r) == tuple:
                role = r[0]
                role_type = r[1]

            # proc role is 'all' trying to remove multiple roles
            if role == 'all':
                # check invalid role_type or None
                if not role_type or role_type not in ['colors', 'colours', 'channels', 'jobs', 'notify', 'all']:

                    embed = discord.Embed(
                        title=None,
                        description=None,
                        color=discord.Color.teal())
                    embed.add_field(
                        name=field_2_name,
                        value=field_2_value)
                    await context.say_as_embed(embed=embed)

                # remove roles by valid provided role_type
                else:

                    # initiate stuff to use
                    to_rmv_roles = {
                        'roles': [],
                        'role_mentions': []
                    }

                    for r in author.roles:
                        if role_type == 'colors' or role_type == 'colours':
                            if r.name in config.AUTOASIGN_COLOR_ROLES:
                                to_rmv_roles['roles'].append(r)
                                to_rmv_roles['role_mentions'].append(r.mention)
                        elif role_type == 'channels':
                            if r.name in config.AUTOASIGN_CHANNEL_ROLES:
                                to_rmv_roles['roles'].append(r)
                                to_rmv_roles['role_mentions'].append(r.mention)
                        elif role_type == 'jobs':
                            if r.name in config.AUTOASIGN_JOB_ROLES:
                                to_rmv_roles['roles'].append(r)
                                to_rmv_roles['role_mentions'].append(r.mention)
                        elif role_type == 'notify':
                            if r.name in config.AUTOASIGN_NOTIFY_ROLES:
                                to_rmv_roles['roles'].append(r)
                                to_rmv_roles['role_mentions'].append(r.mention)
                        elif role_type == 'all':
                            if r.name in config.AUTOASIGN_ROLES:
                                to_rmv_roles['roles'].append(r)
                                to_rmv_roles['role_mentions'].append(r.mention)

                    # remove roles if there are any
                    if to_rmv_roles['roles']:
                        await author.remove_roles(*to_rmv_roles['roles'])
                        mention_roles = ", ".join(to_rmv_roles['role_mentions'])

                        if server.id == config.MSVN_SERVER_ID:
                            remove_roles_done_msg = f'{author.mention}, role {mention_roles} đã được xóa thành công.'
                            no_role_type_found_msg = f'{author.mention}, không có Role nào thuộc loại role `{role_type}`.\n'
                            no_role_type_found_msg += 'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.'
                        elif server.id == config.DAWN_SERVER_ID:
                            remove_roles_done_msg = f'{author.mention}, {mention_roles} has been removed from your roles.'
                            no_role_type_found_msg = f'{author.mention}, role type: `{role_type}` not found. Try using `colors` instead.'

                        await context.say_as_embed(
                            message=remove_roles_done_msg,
                            color='success')
                    else:

                        if server.id == config.MSVN_SERVER_ID:
                            no_role_type_found_msg = f'{author.mention}, không có Role nào thuộc loại role `{role_type}`.\n'
                            no_role_type_found_msg += 'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.'
                        elif server.id == config.DAWN_SERVER_ID:
                            no_role_type_found_msg = f'{author.mention}, role type: `{role_type}` not found. Try using `colors` instead.'

                        await context.say_as_embed(
                            message=no_role_type_found_msg,
                            color='error')

            elif role is not None:

                r = discord.utils.get(message.guild.roles, name=r)

                if server.id == config.MSVN_SERVER_ID:
                    remove_role_done_msg = f'{author.mention}, role {r.mention} đã được xóa thành công.'
                elif server.id == config.DAWN_SERVER_ID:
                    remove_role_done_msg = f'{author.mention}, your {r.mention} role has been removed.'

                if r not in author.roles:
                    await context.say_as_embed(
                        message=no_role_found_msg,
                        color='error')

                else:
                    await author.remove_roles(r)
                    await context.say_as_embed(
                        message=remove_role_done_msg,
                        color='success')

            else:
                await context.say_as_embed(
                    message=wrong_role_name_provided_msg,
                    color='error')

    @commands.command()
    async def list(self, context):
        """Xem danh sách Role có thể tự thêm/xóa"""
        message = context.message
        server = message.guild
        prefix = self.bot.command_prefix

        if server.id == config.MSVN_SERVER_ID:

            embed = discord.Embed(
                title='Danh sách Role có thể tự thêm/xóa',
                description=f'Dùng lệnh `{prefix}role tên_role` để thêm role.\n'
                f'Dùng lệnh `{prefix}rrole tên_role` để xóa role.',
                colour=discord.Color.teal())

            ch_roles = []
            co_roles = []
            no_roles = []
            jo_roles = []

            for role_name in config.AUTOASIGN_CHANNEL_ROLES:
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    ch_roles.append(r.mention)

            for role_name in config.AUTOASIGN_COLOR_ROLES:
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    co_roles.append(r.mention)

            for role_name in config.AUTOASIGN_NOTIFY_ROLES:
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    no_roles.append(r.mention)

            for index, role_name in enumerate(config.AUTOASIGN_JOB_ROLES):
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    jo_roles.append(r.mention)

            embed.add_field(name='Color Roles', value='\n'.join(co_roles))
            embed.add_field(name='Job Roles', value='\n'.join(jo_roles[:24]))
            embed.add_field(name='Job Roles', value='\n'.join(jo_roles[24:]))
            embed.add_field(name='Channel Roles', value='\n'.join(ch_roles))
            embed.add_field(name='Notification Roles', value='\n'.join(no_roles))

        elif server.id == config.DAWN_SERVER_ID:

            dawn_role = discord.utils.get(server.roles, id=364967220193001472)
            collector_role = discord.utils.get(server.roles, id=544542640838934528)

            embed = discord.Embed(
                title='Auto-asign color roles',
                description=f'Use `{prefix}role role_name` to add yourself a **Color Role**.\n'
                f'Use `{prefix}rrole role_name` to remove a color role you have.\n'
                f'**These commands are available for {dawn_role.mention} and {collector_role.mention} only**.',
                colour=discord.Color.teal())

            co_roles = []
            for role_name in config.AUTOASIGN_COLOR_ROLES:
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    co_roles.append(r.mention)

            no_roles = []
            for role_name in config.AUTOASIGN_DAWN_NOTIFY_ROLES:
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    no_roles.append(r.mention)

            ev_roles = []
            for role_name in config.AUTOASIGN_DAWN_EVENT_ROLES:
                r = discord.utils.get(server.roles, name=role_name)
                if r is not None:
                    ev_roles.append(r.mention)

            embed.add_field(name='Color Roles', value='\n'.join(co_roles))
            embed.add_field(name='Event Roles', value='\n'.join(ev_roles))
            embed.add_field(name='Notification Roles', value='\n'.join(no_roles))

        await context.send(embed=embed)

    @_role.error
    @_rrole.error
    async def _handle_errors(self, context, error):
        if context.guild.id == config.DAWN_SERVER_ID:
            dawn_role = discord.utils.get(context.guild.roles, id=364967220193001472)
            collector_role = discord.utils.get(context.guild.roles, id=544542640838934528)
            if context.invoked_with in ['role', 'rrole', 'iam', 'iamn']:
                await context.say_as_embed(
                    message=f'Sorry, only {dawn_role.mention} and {collector_role.mention} '
                    'can use this command. Join us for these awesome colors! '
                    'Or get special roles by participating in events!')
        return  # fail silently


def setup(bot):
    bot.add_cog(Role(bot))
