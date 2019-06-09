import discord
from discord.ext import commands
from francis.utils.role import process_role
from francis.converters import CustomRoleConverter
from utils.user import get_user_obj
import config
from datetime import datetime


def good_for_role_assign(context):
    # Dawn member check
    if context.guild.id == config.DAWN_SERVER_ID:
        author_role_ids = [role.id for role in context.author.roles]
        return any(role_id in config.DAWN_COLOR_CHANGE_ROLE_IDS for role_id in author_role_ids)
    else:
        return True


class Role(commands.Cog):
    """A cog for role management commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='role', aliases=['iam', ])
    @commands.check(good_for_role_assign)
    async def _role(self, context, *, role: commands.Greedy[CustomRoleConverter]):
        """Set Role theo yêu cầu"""

        if context.guild.id == config.MSVN_SERVER_ID:
            add_role_done_msg = (
                f'{context.author.mention} đã nhận được role '
                '{added_role_mention}.'
            )
            role_exists_msg = f'{context.author.mention} có role này rồi nhé.'
        elif context.guild.id == config.DAWN_SERVER_ID:
            add_role_done_msg = (
                f'{context.author.mention}, '
                '{added_role_mention} role has been added.'
            )
            role_exists_msg = f'{context.author.mention}, you already have this role.'

        else:
            return

        if role in context.author.roles:
            await context.say_as_embed(
                description=role_exists_msg,
                color='error')

        else:
            await context.author.add_roles(role)
            await context.say_as_embed(
                description=add_role_done_msg.format(added_role_mention=role.mention),
                color='success')

    @commands.command(name='rrole', aliases=['iamn', ])
    @commands.check(good_for_role_assign)
    async def _rrole(self, context, *, role: commands.Greedy[CustomRoleConverter]):
        """Xóa Role theo yêu cầu
        """

        if context.guild.id == config.MSVN_SERVER_ID:
            remove_role_done_msg = (
                f'{context.author.mention}, role '
                '{removed_role_mentions} đã được xóa thành công.'
            )
            no_role_found_msg = (
                f'{context.author.mention} không có role này.\n'
                'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.'
            )
        elif context.guild.id == config.DAWN_SERVER_ID:
            remove_role_done_msg = (
                f'{context.author.mention}, your '
                '{removed_role_mentions} role(s) have been removed.'
            )
            no_role_found_msg = f'{context.author.mention}, you don\'t have the specified role(s).'

        else:
            return

        if role not in context.author.roles:
            await context.say_as_embed(
                description=no_role_found_msg,
                color='error')

        else:
            await context.author.remove_roles(role)
            await context.say_as_embed(
                description=remove_role_done_msg.format(removed_role_mentions=role.mention),
                color='success')

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

            dawn_role_mentions = [server.get_role(role_id).mention for role_id in config.DAWN_COLOR_CHANGE_ROLE_IDS]

            embed = discord.Embed(
                title='Auto-asign color roles',
                description=f'Use `{prefix}role role_name` to add yourself a Role.\n'
                f'Use `{prefix}rrole role_name` to remove a Role you have.',
                colour=discord.Color.teal())

            embed.add_field(
                name='Availability',
                value=f'These commands are available to {", ".join(dawn_role_mentions)} only.',
            )

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

        else:
            return

        await context.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        dawn = self.bot.get_guild(config.DAWN_SERVER_ID)
        if not dawn:
            return

        dawn_rfr = {}
        for emoji_id, role_id in zip(config.DAWN_REACT_FOR_ROLE_EMOJI_IDS, config.DAWN_REACT_FOR_ROLE_ROLE_IDS):
            dawn_rfr.update({int(emoji_id): dawn.get_role(int(role_id))})

        member = dawn.get_member(payload.user_id)
        if not member:
            return

        # SAO DED role
        if payload.emoji.name == '\N{REGIONAL INDICATOR SYMBOL LETTER F}':
            if payload.message_id != 553086377562996767:
                return

            # role add
            died_role = dawn.get_role(553084583265042434)
            monument_channel = dawn.get_channel(553086153553870858)
            user_obj = get_user_obj(member)
            await member.add_roles(died_role)
            embed = discord.Embed(
                title='',
                description=
                f'{member.mention}',
                timestamp=datetime.utcnow(),
                color=discord.Color.darker_grey()
            )
            # sends message
            msg = await monument_channel.send(embed=embed)

            # update user info
            user_obj.monument_message_id = msg.id
            user_obj.monument_channel_id = msg.channel.id
            user_obj.save()

        if payload.emoji.id in dawn_rfr:

            if payload.message_id != config.DAWN_REACT_FOR_ROLE_MESSAGE_ID:
                return

            await member.add_roles(dawn_rfr[payload.emoji.id])

            channel = dawn.get_channel(payload.channel_id)
            embed = discord.Embed(
                title='',
                description=
                f'{member.mention} has been given the '
                f'{dawn_rfr[payload.emoji.id].mention} role.',
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed, delete_after=5)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        dawn = self.bot.get_guild(config.DAWN_SERVER_ID)
        if not dawn:
            return

        dawn_rfr = {}
        for emoji_id, role_id in zip(config.DAWN_REACT_FOR_ROLE_EMOJI_IDS, config.DAWN_REACT_FOR_ROLE_ROLE_IDS):
            dawn_rfr.update({int(emoji_id): dawn.get_role(int(role_id))})

        member = dawn.get_member(payload.user_id)
        if not member:
            return

        # SAO DED role
        if payload.emoji.name == '\N{REGIONAL INDICATOR SYMBOL LETTER F}':
            if payload.message_id != 553086377562996767:
                return

            # role removal
            died_role = dawn.get_role(553084583265042434)
            user_obj = get_user_obj(member)
            await member.remove_roles(died_role)
            # msg removal
            msg_db = await user_obj.fetch_message(dawn)
            if msg_db:
                await msg_db.delete()

            user_obj.monument_message_id = None
            user_obj.monument_channel_id = None
            user_obj.save()

        if payload.emoji.id in dawn_rfr:
            if payload.message_id != config.DAWN_REACT_FOR_ROLE_MESSAGE_ID:
                return

            member = dawn.get_member(payload.user_id)
            await member.remove_roles(dawn_rfr[payload.emoji.id])

            channel = dawn.get_channel(payload.channel_id)
            embed = discord.Embed(
                title='',
                description=
                f'{dawn_rfr[payload.emoji.id].mention} role '
                f'has been removed from {member.mention}.',
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed, delete_after=5)

    @_role.error
    @_rrole.error
    async def _handle_errors(self, context, error):
        message = context.message
        author = message.author
        server = message.guild
        prefix = self.bot.command_prefix

        if server.id == config.MSVN_SERVER_ID:

            add_role_help_title = f'Cú pháp: `{prefix}role tên_role`'
            add_role_help_desc = f'Dùng lệnh này để yêu cầu bot thêm Role cho bạn. Nhập lệnh `{prefix}list` để xem danh sách Role.'

            remove_role_help_title = f'Cú pháp xóa Role: `{prefix}rrole tên_role`'
            remove_role_help_desc = (
                f'Nhập lệnh `{prefix}list` để xem danh sách Role có thể xóa.\n'
                'Click (PC) hoặc Nhấn giữ (Mobile) vào **tên của bạn** để xem những Role bạn đang có.'
            )
            wrong_role_name_provided_msg = (
                f'{author.mention}, role này không tồn tại hoặc không tự xử được nha. '
                f'Gõ `{prefix}list` để xem các Role.'
            )
        elif server.id == config.DAWN_SERVER_ID:
            dawn_role_mentions = [server.get_role(role_id).mention for role_id in config.DAWN_COLOR_CHANGE_ROLE_IDS]

            add_role_help_title = f'Format: `{prefix}role role_name`'
            add_role_help_desc = (
                f'Use this command to assign a Role. Type `{prefix}list` to see a full list of available roles.\n\n'
                f'**This command is available for {", ".join(dawn_role_mentions)} only**.'
            )

            remove_role_help_title = f'`{prefix}rrole role_name`'
            remove_role_help_desc = (
                f'Use this command to remove a Role. Type `{prefix}list` to see a full list of available roles.\n\n'
                f'**This command is available for {", ".join(dawn_role_mentions)} only**.'
            )

            wrong_role_name_provided_msg = (
                f'{author.mention}, this role does not exist, or not removeable. '
                f'Type `{prefix}list` to see a full list of available roles.'
            )

        else:
            return

        if isinstance(error, commands.CheckFailure):
            dawn_role_mentions = [context.guild.get_role(role_id).mention for role_id in config.DAWN_COLOR_CHANGE_ROLE_IDS]

            if context.invoked_with in ['role', 'rrole', 'iam', 'iamn']:
                await context.say_as_embed(
                    description=f'Sorry, only {", ".join(dawn_role_mentions)} '
                    'can use this command. Join us for these awesome colors! '
                    'Or get special roles by participating in events!')

        elif isinstance(error, commands.MissingRequiredArgument):
            if context.invoked_with in ['role', 'iam']:
                await context.say_as_embed(
                    title=add_role_help_title,
                    description=add_role_help_desc,
                )
            else:
                await context.say_as_embed(
                    title=remove_role_help_title,
                    description=remove_role_help_desc,
                )

        elif isinstance(error, commands.BadArgument):
            await context.say_as_embed(
                wrong_role_name_provided_msg,
                color='error',
            )


def setup(bot):
    bot.add_cog(Role(bot))
