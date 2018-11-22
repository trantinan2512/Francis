import discord
from discord.ext import commands
import config
import asyncio


class CustomContext(commands.Context):
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
            message = await self.send(embed=embed)
        else:
            message = await self.send(embed=embed)

        return message


class CustomBot(commands.Bot):

    async def on_message(self, message):
        ctx = await self.get_context(message, cls=CustomContext)
        await self.invoke(ctx)

    async def on_raw_reaction_add(self, payload, message_id, channel_id, user_id):

        if message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('role')
        elif message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('notify')

        react_role_name = None
        for role_name, emoji in zip_list:
            if payload.name == emoji:
                react_role_name = role_name
                break

        if react_role_name is None:
            return

        channel = self.get_channel(channel_id)
        if channel is None:
            return

        guild = channel.guild
        member = guild.get_member(user_id)
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

        if message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            await member.add_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} đã nhận được danh hiệu **{react_role.mention}**')
            await asyncio.sleep(5)
            await response.delete()
        elif message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            await member.add_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} sẽ nhận được thông báo khi ping **{react_role.mention}** nữa.')
            await asyncio.sleep(5)
            await response.delete()

    async def on_raw_reaction_remove(self, payload, message_id, channel_id, user_id):

        if message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('role')
        elif message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
            zip_list = self.zip_role_emoji_lists('notify')

        react_role_name = None
        for role_name, emoji in zip_list:
            if payload.name == emoji:
                react_role_name = role_name
                break

        if react_role_name is None:
            return

        channel = self.get_channel(channel_id)
        if channel is None:
            return

        guild = channel.guild
        member = guild.get_member(user_id)
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

        if message_id == config.REACT_FOR_ROLE_MESSAGE_ID:
            await member.remove_roles(react_role)
            response = await self.say_as_embed(
                channel, message=f'{member.mention} đã được xóa bỏ danh hiệu **{react_role.mention}**.')
            await asyncio.sleep(5)
            await response.delete()
        elif message_id == config.REACT_FOR_NOTIFICATION_ROLE_MESSAGE_ID:
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
