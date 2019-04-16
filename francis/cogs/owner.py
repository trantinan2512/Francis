# import discord
from discord.ext import commands
from django.conf import settings


class OwnerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.path = 'francis.cogs.'

    async def is_owner(ctx):
        return ctx.author.id == 209551520008503297

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
    @commands.check(is_owner)
    async def load(self, ctx, *, module):
        """Loads a module."""
        self.bot.load_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.check(is_owner)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        self.bot.unload_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.check(is_owner)
    async def _reload(self, ctx, *, module):
        """Reloads a module."""

        self.bot.unload_extension(f'{self.path}{module}')
        self.bot.load_extension(f'{self.path}{module}')
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='test', hidden=True)
    @commands.check(is_owner)
    async def _test_command(self, ctx):
        """Test command"""

        emojis = '```\n'
        for emoji in ctx.guild.emojis:
            emojis += f'\'{emoji.name}\' : {emoji.id},\n'
        emojis += '```'

        await ctx.send(emojis)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))
