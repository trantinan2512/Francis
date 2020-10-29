import asyncio
import traceback

import discord
from discord.ext import commands
from django.conf import settings

import config

# intents update
intents = discord.Intents.default()
intents.members = True

class CustomContext(commands.Context):
    async def say_as_embed(
            self,
            description=None, title=None,
            embed=None, color='info',
            delete_after=None,
            footer_text=None,
            image_url=None,
            thumb_url=None,
    ):
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
                description=description,
                colour=color)

            if image_url:
                embed.set_image(url=image_url)

            if thumb_url:
                embed.set_thumbnail(url=thumb_url)

            if footer_text:
                embed.set_footer(text=footer_text)

        message = await self.send(embed=embed, delete_after=delete_after)

        return message


class CustomBot(commands.Bot):

    async def on_ready(self):
        print('------')
        print(f'Logged in as: {self.user.name} (ID: {self.user.id})')
        print('------')
        if not settings.DEBUG:
            # change this for the 'Playing xxx' status
            presence = f'Prefix: {config.BOT_PREFIX}'
        else:
            presence = f'sensei anone'
        await self.change_presence(activity=discord.Game(name=presence))
        await self.load_tasks()

    async def load_tasks(self):
        tasks = []
        if config.DEBUG:
            tasks += [
                # 'francis.tasks.tiki',
                # 'francis.tasks.socials',
                # 'francis.tasks.crawlers'
            ]
        else:
            tasks += [
                'francis.tasks.socials',
                'francis.tasks.crawlers'
            ]
        for task in tasks:
            try:
                self.load_extension(task)
            except Exception as e:
                traceback.print_exc()

    async def on_message(self, message):
        ctx = await self.get_context(message, cls=CustomContext)
        await self.invoke(ctx)

    async def on_member_join(self, member):
        """Says when a member joined."""
        if member.guild.id != config.MSVN_SERVER_ID:
            return

        welcome_channel = self.get_channel(453886339570597890)
        rules_channel = self.get_channel(453566033190584321)
        intro_channel = self.get_channel(455025500071526401)
        francis_channel = self.get_channel(454310191962390529)
        role_channel = self.get_channel(472965546485481473)

        message = (
                f'Chào mừng **{member.mention}** đã đến với **{member.guild.name}**!\n\n' +
                f'Dưới đây là hướng dẫn tương tác với group nhé!\n' +
                f'» Đọc {rules_channel.mention} ở đây (có hướng dẫn game).\n' +
                f'» {intro_channel.mention} giới thiệu bản thân.\n' +
                f'» Qua kênh {role_channel.mention} để nhận danh hiệu ứng với game mình đang chơi!\n\n' +
                f'Nhập lệnh `{self.command_prefix}help` ở kênh {francis_channel.mention} để được hỗ trợ thêm nhé.')

        await welcome_channel.send(message)

    async def on_raw_reaction_add(self, payload):

        if payload.message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('role')
        elif payload.message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('notify')
        else:
            # print('ERROR - Message ID not found.')
            return

        react_role_name = None
        for role_name, emoji in zip_list:
            if payload.name == emoji:
                react_role_name = role_name
                break

        if react_role_name is None:
            return

        channel = self.get_channel(payload.channel_id)
        if channel is None:
            return

        guild = channel.guild
        member = guild.get_member(payload.user_id)
        if member is None:
            response = await self.say_as_embed(channel, message='Unable to find the user that reacted.', color='error')
            await asyncio.sleep(5)
            await response.delete()
            return

        react_role = discord.utils.get(guild.roles, name=react_role_name)
        if react_role is None:
            response = await self.say_as_embed(
                channel, message=f'Unable to find role named **{react_role_name}**', color='error')
            await asyncio.sleep(5)
            await response.delete()
            return

        if payload.message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            await member.add_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} đã nhận được danh hiệu **{react_role.mention}**')
            await asyncio.sleep(5)
            await response.delete()
        elif payload.message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            await member.add_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} sẽ nhận được thông báo khi ping **{react_role.mention}**.')
            await asyncio.sleep(5)
            await response.delete()

    async def on_raw_reaction_remove(self, payload):

        if payload.message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('role')
        elif payload.message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('notify')
        else:
            # print('ERROR - Message ID not found.')
            return

        react_role_name = None
        for role_name, emoji in zip_list:
            if payload.name == emoji:
                react_role_name = role_name
                break

        if react_role_name is None:
            return

        channel = self.get_channel(payload.channel_id)
        if channel is None:
            return

        guild = channel.guild
        member = guild.get_member(payload.user_id)
        if member is None:
            response = await self.say_as_embed(channel, message='Unable to find the user that reacted.', color='error')
            await asyncio.sleep(5)
            await response.delete()
            return

        react_role = discord.utils.get(guild.roles, name=react_role_name)
        if react_role is None:
            response = await self.say_as_embed(
                channel, message=f'Unable to find role named **{react_role_name}**', color='error')
            await asyncio.sleep(5)
            await response.delete()
            return

        if payload.message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            await member.remove_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} đã được xóa bỏ danh hiệu **{react_role.mention}**.')
            await asyncio.sleep(5)
            await response.delete()
        elif payload.message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            await member.remove_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} sẽ không nhận thông báo khi ping **{react_role.mention}** nữa.')
            await asyncio.sleep(5)
            await response.delete()

    def zip_role_emoji_lists(self, role_kind):
        if role_kind == 'role':
            r_list = ['GMS', 'GMSM', 'GMS2']
            e_list = ['🖥', '📱', '🍁']
        else:
            r_list = ['Notify GMS', 'Notify GMSM']
            e_list = ['🖥', '📱']

        new = zip(r_list, e_list)
        return new

    async def say_as_embed(self, channel, message=None, title=None, embed=None, color='info'):
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
            message = await channel.send(embed=embed)
        else:
            message = await channel.send(embed=embed)

        return message

    async def on_command_error(self, context, error):

        ignored = (
            commands.CommandNotFound,
            commands.PrivateMessageOnly
        )
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.MissingRole):
            await context.say_as_embed(
                f'{context.author.mention}, you must have '
                f'**<@&{error.missing_role}>** role to use this command!',
                color='error', delete_after=5)
            await context.message.delete()
            return

        if isinstance(error, commands.MissingAnyRole):
            missing_roles_mention = ", or ".join([f"**<@&{role}>**" for role in error.missing_roles])
            await context.say_as_embed(
                f'{context.author.mention}, you must have '
                f'{missing_roles_mention} roles to use this command!',
                color='error', delete_after=5)
            await context.message.delete()
            return

        # missing required argument and is not a help command
        # if isinstance(error, commands.MissingRequiredArgument) and context.command.qualified_name != 'help':
        #     prefix = context.prefix
        #     command_name = context.invoked_with
        #     embed = discord.Embed(
        #         title=f'How to use the `{command_name}` command',
        #         description=
        #         context.command.help.format(prefix=prefix, command_name=command_name),
        #         color=config.EMBED_DEFAULT_COLOR
        #     )
        #     await context.send(embed=embed)
        #     return

        if isinstance(error, commands.BadArgument):
            await context.say_as_embed(str(error), color='error')
            return

        if isinstance(error, commands.CommandInvokeError):
            # shoutout if it's not silent
            if not getattr(error.original, 'silent', False):
                await context.say_as_embed(str(error.original), color='error')
                return

        if settings.DEBUG:
            error = getattr(error, 'original', error)
            # shoutout if it's not silent
            if not getattr(error, 'silent', False):
                tb_obj = getattr(error, '__traceback__')
                tb = '\n'.join(traceback.format_tb(tb_obj))
                traceback.print_tb(tb_obj)
                print(error)
                if context.invoked_with != 'help':
                    await context.send(f'```bash\n{tb}\n{error}```')

        await super().on_command_error(context, error)
