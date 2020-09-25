# import discord
import sys

from discord.ext import commands
from discord.ext.commands import Greedy, MessageConverter

import config


class OwnerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.path = 'francis.cogs.'
        self.path2 = 'francis.tasks.'

    @commands.command(aliases=['prunenorole', 'prunenr'])
    @commands.is_owner()
    async def _prune_no_role_members(self, context):

        to_be_pruned = 'Below is a list of members to be pruned with no role assigned:\n'
        for member in context.guild.members:
            if member.top_role.name == '@everyone':
                to_be_pruned += f'• {member.mention}\n'

        step = 1000
        while len(to_be_pruned) > step:
            text = to_be_pruned[step - 1000:step]
            step += 1000
            await context.say_as_embed(
                f'{text}'
            )
        await context.say_as_embed('Respond with **yes** to remove these members. Responde **no** to cancel.')

        def check_same_author(message):
            return message.author == context.author

        confirm = await self.bot.wait_for('message', timeout=60, check=check_same_author)
        if confirm.content.lower() not in ['y', 'yes']:
            await context.say_as_embed('No one has been removed.', color='error')
            return

        for member in context.guild.members:
            if member.top_role.name == '@everyone':
                await context.guild.kick(member, reason='No role given -> raid member -> kicked')

        await context.say_as_embed('Successfully updated.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        self.bot.load_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        self.bot.unload_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(f'{self.path}{module}')
            self.bot.load_extension(f'{self.path}{module}')
        except Exception:
            self.bot.unload_extension(f'{self.path2}{module}')
            self.bot.load_extension(f'{self.path2}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='test', hidden=True)
    @commands.is_owner()
    async def _test_command(self, context, messages: Greedy[MessageConverter] = None):
        """
        Test command
        """
        # print(messages)
        # for message in messages:
        #     emoji_ids = config.PONPON_ROLE_REACT_EMOJI_IDS
        #     for emoji_id in emoji_ids:
        #         print(emoji_id)
        #         emoji = context.bot.get_emoji(id=emoji_id)
        #         await message.add_reaction(emoji)
        #         break
        # sends chunked emojis and reacts to that message with these emojis
        emoji_ids = config.PONPON_ROLE_REACT_EMOJI_IDS
        for chunk in chunks(emoji_ids, 10):
            message = await context.send(' '.join(f'<:something:{emoji_id}>' for emoji_id in chunk))
            for emoji_id in chunk:
                emoji = context.bot.get_emoji(id=emoji_id)
                await message.add_reaction(emoji)

    @commands.command(hidden=True, aliases=['q'])
    @commands.is_owner()
    async def restart(self, ctx):
        """Restarts the bot and exit the system"""
        await ctx.send('Restarting in 10 seconds...')
        await self.bot.logout()
        sys.exit(6)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def setup(bot):
    bot.add_cog(OwnerCommands(bot))
