from pprint import pprint
import json
import asyncio
import operator

import discord
from discord.ext import commands

from utils.db import initialize_db
import config

from dateparser import parse
from django.db.models import F


from web.apps.users.models import DiscordUser


class Admin:
    """A cog for Admin-only commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db = initialize_db()

    def is_me(ctx):
        return ctx.author.id == config.MY_ID

    def is_mod(ctx):
        author = ctx.author
        server = ctx.server
        # MSVN Community server
        if server.id == 453555802670759947:
            mod_gms_role = discord.utils.get(author.roles, name='Mod GMS')
            mod_gmsm_role = discord.utils.get(author.roles, name='Mod GMSM')
            super_mod_role = discord.utils.get(author.roles, name='Super Mod')
            if mod_gms_role or mod_gmsm_role or super_mod_role:
                return True
            else:
                return False
        else:
            # Vice commander id or myself
            return author.id == config.MY_ID or author.top_role.id == 373667156468170755

    @commands.command(name='e')
    @commands.check(is_me)
    async def _emoji_sender(self, context, *, emoji: str):
        await context.message.delete()

        if emoji == 'yuianone':
            yui1 = discord.utils.get(self.bot.emojis, name='yuianone1')
            yui2 = discord.utils.get(self.bot.emojis, name='yuianone2')
            yui3 = discord.utils.get(self.bot.emojis, name='yuianone3')
            yui4 = discord.utils.get(self.bot.emojis, name='yuianone4')
            await context.send(f'{yui1}{yui2}\n{yui3}{yui4}')
            return

        emoji = discord.utils.get(self.bot.emojis, name=emoji)
        if not emoji:
            msg = await context.say_as_embed(f'Unable to find any emojis with argument `{emoji}`.')
            await asyncio.sleep(3)
            await msg.delete()
            return
        await context.send(emoji)

    @commands.command(name='clear')
    @commands.check(is_me)
    async def clear_messages(self, context, limit=100, check=None):
        """Lệnh xóa tin nhắn
        """
        channel = context.channel

        if check is None:
            messages = []
            async for message in channel.history(limit=limit):
                messages.append(message)

            note = await context.send(f'Tiến hành xóa {len(messages)} tin nhắn :hourglass_flowing_sand:')
            chunks = [messages[x:x + 100] for x in range(0, len(messages), 100)]
            counter = 0
            for chunk in chunks:
                await channel.delete_messages(chunk)
                counter += len(chunk)
                if chunk != chunks[-1]:
                    await note.edit(
                        content=f'Xóa thành công {counter}/{len(messages)} tin nhắn :hourglass_flowing_sand:')
                else:
                    await note.edit(
                        content=''
                        f'Xóa thành công {counter}/{len(messages)} tin nhắn :white_check_mark:\n'
                        '*Tự động xóa tin nhắn này sau 10 giây*')
                    print(f'Deleted {counter}/{len(messages)} messages.')

            await asyncio.sleep(10)
            await note.delete()

        else:

            def is_bot(m):
                return m.author == self.bot.user

            deleted = await channel.purge(limit=limit, check=is_bot)
            await channel.send(f'Deleted {len(deleted)} message(s)')

    @commands.command(name='countmsg')
    @commands.check(is_me)
    async def count_users_messages(self, context, prefix=None, limit=5000):
        """Lệnh đếm số tin nhắn trong kênh
        Nếu có 'prefix', chỉ đếm những tin nhắn có prefix.
        KHÔNG đếm những tin nhắn của bot (có role Artificial Intelligence)
        """

        channel = context.channel
        ai_role = discord.utils.get(context.server.roles, name='Artificial Intelligence')

        note = await channel.send(f'Đang xử lý...')
        counter = 0
        data_dict = {}
        async for message in self.bot.logs_from(channel, limit=limit):

            # excludes bot (Bot with Artificial Intelligence Role)
            if ai_role not in message.author.roles:

                # prefix counter
                if prefix is not None:
                    if message.content.startswith(prefix):
                        if message.author.name in list(data_dict.keys()):
                            data_dict[message.author.name] += 1
                        else:
                            data_dict.update({message.author.name: 1})
                        counter += 1
                # no prefix
                else:
                    if message.author.name in list(data_dict.keys()):
                        data_dict[message.author.name] += 1
                    else:
                        data_dict.update({message.author.name: 1})
                    counter += 1

        sorted_data = sorted(data_dict.items(), key=operator.itemgetter(1), reverse=True)

        embed = discord.Embed(
            title='Kết quả',
            description=f'Tổng số tin nhắn được xử lý: `{counter}`',
            color=discord.Color.teal())

        for index, item in enumerate(sorted_data, start=1):
            if index == 1:
                rank_indicator = ':first_place:'
            elif index == 2:
                rank_indicator = ':second_place:'
            elif index == 3:
                rank_indicator = ':third_place:'
            elif index in [4, 5]:
                rank_indicator = ':ribbon:'
            else:
                rank_indicator = ''
            embed.add_field(
                name=f'{item[0]} {rank_indicator}',
                value=f'Số tin nhắn: `{item[1]}`')

        await self.bot.delete_message(note)
        await context.say_as_embed(embed=embed)

    @commands.command(name='playing')
    @commands.check(is_me)
    async def change_bot_presence(self, context, *, presence: str):
        await self.bot.change_presence(game=discord.Game(name=presence))

    @commands.command(name='sc')
    @commands.check(is_mod)
    async def event_scheduler(self, context, *, data=None):
        to_delete_messages = []
        prefix = self.bot.command_prefix
        timeout = 30
        timeout_msg = f'Session timed out. Please start over by typing `{prefix}schedule start`.'
        # maplestory
        if context.message.server.id == '453555802670759947':
            schedule_db = self.db.worksheet('schedules_ms')
        # saomd Dawn
        elif context.message.server.id == '364323564737789953':
            schedule_db = self.db.worksheet('schedules_saomd')

        def check_same_author(message):
            return message.author == context.author

        # display help text when no/wrong data provided
        if data is None \
                or '--' not in data \
                and not data.startswith('start') \
                and not data.startswith('list'):
            await context.send(
                '**Schedule Function 101**\n'
                f'`{prefix}sc` : show this message.\n'
                f'`{prefix}sc list` : show a list of to-be-announced events.\n'
                f'`{prefix}sc start` : start listening for Event Name and Event Datetime. '
                'Follow the steps to complete scheduling.\n'
                f'`{prefix}sc event_name -- event_date_time` : shortcut to schedule events more quickly.'
            )

        # shorthand with `schedule [event name] -- [date time]
        elif '--' in data:
            to_delete_messages.append(context.message)
            event_name, event_datetime = data.split('--', 1)
            event_name = event_name.strip()
            parsed_datetime = parse(event_datetime, settings={'DATE_ORDER': 'DMY'})
            if parsed_datetime is None:
                msg = await context.send('Cannot recognize the Date Time provided. Please try again.')
                to_delete_messages.append(msg)
                pass
            else:
                if parsed_datetime.tzinfo is not None:
                    str_datetime = parsed_datetime.strftime('%I:%M:%S %p %d/%m/%Y (%Z)')
                else:
                    str_datetime = parsed_datetime.strftime('%I:%M:%S %p %d/%m/%Y (UTC)')

                msg = await context.send(
                    'Here is the data you provided (date time format: `HH:MM:SS PP dd/mm/yyyy (Timezone)`):'
                    f'```Event Name: {event_name}\n'
                    f'Event Date: {str_datetime}```'
                    'Is this correct? (yes/no)'
                )
                to_delete_messages.append(msg)

                done = False

                while done is not True:
                    try:
                        confirm = await self.bot.wait_for('message', check=check_same_author, timeout=timeout)
                    except asyncio.TimeoutError:
                        msg = await context.send(f'Session timed out. Please start over.')
                        to_delete_messages.append(msg)
                        break
                    to_delete_messages.append(confirm)

                    if confirm.content.lower().startswith('y'):

                        schedule_db.insert_row([event_name, str_datetime], index=2)

                        msg = await context.send('Done! Thanks.')
                        to_delete_messages.append(msg)
                        done = True
                    elif confirm.content.lower().startswith('n'):
                        msg = await context.send(f'No schedule created. Please try again.')
                        to_delete_messages.append(msg)
                        done = True
                    else:
                        msg = await context.send(f'Please type either `yes (y)` or `no (n)`.')
                        to_delete_messages.append(msg)

        # start listening to the user with `schedule start`
        elif data.startswith('start'):
            to_delete_messages.append(context.message)
            msg = await context.send('Please provide the Event Name')
            to_delete_messages.append(msg)

            event_name = await self.bot.wait_for('message', check=check_same_author, timeout=timeout)
            if event_name is None:
                msg = await context.send(timeout_msg)
                to_delete_messages.append(msg)
                pass
            to_delete_messages.append(event_name)

            msg = await context.send('Please provide the Date and Time for the event. Provide the timezone also, default is UTC.')
            to_delete_messages.append(msg)

            event_datetime = await self.bot.wait_for('message', check=check_same_author, timeout=timeout)
            if event_datetime is None:
                msg = await context.send(timeout_msg)
                to_delete_messages.append(msg)
                pass
            to_delete_messages.append(event_datetime)

            parsed_datetime = parse(event_datetime.content, settings={'DATE_ORDER': 'DMY'})
            while parsed_datetime is None:

                msg = await context.send('Please provide a correct Date and Time (default timezone: UTC). Or type `quit` to exit.')
                to_delete_messages.append(msg)

                event_datetime = await self.bot.wait_for('message', check=check_same_author, timeout=timeout)
                if event_datetime is None:
                    msg = await context.send(timeout_msg)
                    to_delete_messages.append(msg)
                    break
                to_delete_messages.append(event_datetime)

                if event_datetime.content == 'quit':
                    msg = await context.send('Successfully terminated.')
                    to_delete_messages.append(msg)
                    return
                else:
                    parsed_datetime = parse(event_datetime.content, settings={'DATE_ORDER': 'DMY'})

            if parsed_datetime is not None:

                if parsed_datetime.tzinfo is not None:
                    str_datetime = parsed_datetime.strftime('%I:%M:%S %p %d/%m/%Y (%Z)')
                else:
                    str_datetime = parsed_datetime.strftime('%I:%M:%S %p %d/%m/%Y (UTC)')

                msg = await context.send(
                    'Here is the data you provided (date time format: `HH:MM:SS PP dd/mm/yyyy (Timezone)`):'
                    f'```Event Name: {event_name.content}\n'
                    f'Event Date: {str_datetime}```'
                    'Is this correct? (yes/no)'
                )
                to_delete_messages.append(msg)

                done = False

                while done is not True:
                    confirm = await self.bot.wait_for('message', check=check_same_author, timeout=timeout)
                    if confirm is None:
                        msg = await context.send(timeout_msg)
                        to_delete_messages.append(msg)
                        pass
                    to_delete_messages.append(confirm)

                    if confirm.content.lower().startswith('y'):

                        schedule_db.insert_row([event_name.content, str_datetime], index=2)

                        msg = await context.send('Done! Thanks.')
                        to_delete_messages.append(msg)
                        done = True
                    elif confirm.content.lower().startswith('n'):
                        msg = await context.send(f'No schedule created. Please start over by typing `{prefix}schedule start`.')
                        to_delete_messages.append(msg)
                        done = True
                    else:
                        msg = await context.send(f'Please type either `yes (y)` or `no (n)`.')
                        to_delete_messages.append(msg)
        elif data.startswith('list'):
            # from the list of db show it here
            records = schedule_db.get_all_records()
            if records:
                posted_counter = 0
                embed = discord.Embed(
                    title='To be announced events:',
                    description='```'
                    f'Command: {prefix}sc list\n'
                    f'Format : HH:MM:SS PP dd/mm/yyyy (Timezone)```',
                    color=discord.Color.blue())

                for record in records:
                    if record['posted']:
                        posted_counter += 1
                    else:
                        embed.add_field(
                            name=f'{record["event_name"]}',
                            value=f'{record["date_time"]}',
                            inline=False)
                if posted_counter == len(records):
                    await context.send('No events available.')
                else:
                    await context.say_as_embed(embed=embed)
            else:
                await context.send('Empty schedules.')

        # delete messages generated by scheduling
        if len(to_delete_messages) != 0:
            note = await context.send(f'The above messages ({len(to_delete_messages)}) will be deleted in 10 seconds'
                                      ':hourglass_flowing_sand:')
            await asyncio.sleep(10)
            await self.bot.delete_messages(to_delete_messages)
            await note.edit('Done :white_check_mark:')
            await asyncio.sleep(5)
            await note.delete()

    @commands.command(name='give')
    @commands.check(is_me)
    async def give_credit(self, context, item, to: int, amount):
        await self.bot.delete_message(context.message)
        if item.lower() in ['cr', 'pl', 'crystal']:
            try:
                user = DiscordUser.objects.get(discord_id=to)
            except DiscordUser.DoesNotExist:
                note = await context.send(f'The user with ID: {to} does not exist.')
                await asyncio.sleep(5)
                await self.bot.delete_message(note)

            user.gacha_info.crystal_owned = F('crystal_owned') + int(amount)
            user.gacha_info.save()

            discord_user = await self.bot.get_user_info(to)
            amount = '{:,}'.format(int(amount))
            await context.send(f'{discord_user.mention} has been credited **{amount} Crystals**.')

    @commands.command(name='grcc')
    @commands.check(is_me)
    async def get_roles_color_code(self, context):

        await context.message.delete()
        ms_server = self.bot.get_server(453555802670759947)
        dawn_server = self.bot.get_server(364323564737789953)

        for ms_role in ms_server.roles:
            if ms_role.name in config.AUTOASIGN_COLOR_ROLES:
                role_names = []
                for dn_role in dawn_server.roles:
                    role_names.append(dn_role.name)
                if ms_role.name in role_names:
                    pass
                else:
                    new_role = await self.bot.create_role(
                        server=dawn_server, name=ms_role.name, color=ms_role.color, hoist=False, mentionable=False)
                    print(f'Created role: {new_role.name} in server: {dawn_server.name}')

    # @clear_messages.error
    # @count_users_messages.error
    # @change_bot_presence.error
    # @event_scheduler.error
    # async def clear_messages_error(self, error, context):
    #     print(error)
    #     return  # fail silently


def setup(bot):
    bot.add_cog(Admin(bot))
