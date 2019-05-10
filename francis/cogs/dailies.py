from discord.ext import commands
import discord
from utils.validators import validate_input
from francis.converters import GameCodeConverter
from web.apps.dailies.models import HonkaiImpactDaily


class DailyManagementCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def is_owner(ctx):
        return ctx.author.id == 209551520008503297

    @commands.command(name='daily')
    @commands.is_owner()
    async def _update_or_create_dailies(
            self, context,
            game: GameCodeConverter,
            emoji: str, *, description: str):
        if game == 'Honkai Impact 3rd':
            hi3_daily, created = HonkaiImpactDaily.objects.update_or_create(
                emoji=emoji,
                defaults={
                    'description': description
                }
            )

            embed = discord.Embed(
                title='',
                description=
                f'• Emoji: {hi3_daily.parse_emoji(context.bot)}\n'
                f'• Description: {description}',
                color=discord.Color.dark_magenta()
            )

            embed.title = 'New Daily Task Item Created' if created else 'Daily Task Item Updated'
            await context.say_as_embed(embed=embed)

    @commands.command(name='rdaily')
    @commands.is_owner()
    async def _remove_dailies(
            self, context,
            game: GameCodeConverter,
            emoji: str):

        if game == 'Honkai Impact 3rd':
            try:
                hi3_daily = HonkaiImpactDaily.objects.get(emoji=emoji)
            except HonkaiImpactDaily.DoesNotExist:
                await context.say_as_embed(
                    f'Daily for {game} with emoji `{emoji}` does not exist',
                    color='error'
                )
                return

            item = HonkaiImpactDaily.objects.exclude(message_id=None).first()
            to_remove_emoji = hi3_daily.parse_emoji(context.bot)
            message = await item.fetch_message(context.bot) if item else None

            await context.say_as_embed(
                f'You are about to remove the daily task with the below info:\n'
                f'• Emoji: {to_remove_emoji}\n'
                f'• Message: {f"[Jump]({message.jump_url})" if message else "N/A"}',
                footer_text='Proceed to deletion? (y/n)'
            )

            response = await validate_input(context, inputs=['y', 'yes'])
            if not response:
                return

            if message and to_remove_emoji:
                for reaction in message.reactions:
                    if to_remove_emoji == reaction.emoji:
                        async for user in reaction.users():
                            await reaction.remove(user)
                        break
                extras = f'Reactions for {to_remove_emoji} removed.'
            else:
                extras = f'Message and/or the Emoji was not found.'

            embed = discord.Embed(
                title='Daily Task Deleted',
                description=
                f'• Emoji: {hi3_daily.parse_emoji(context.bot)}\n'
                f'• Extras: {extras}',
                color=discord.Color.dark_magenta()
            )

            await context.say_as_embed(embed=embed)

            hi3_daily.delete()

    @_update_or_create_dailies.error
    @_remove_dailies.error
    async def _error_handler(self, context, error):

        if isinstance(error, commands.BadArgument):
            await context.say_as_embed(str(error), color='error')

        if isinstance(error, commands.MissingRequiredArgument):
            prefix = context.prefix

            if context.invoked_with == 'daily':
                await context.say_as_embed(
                    title=f'How to use `{context.invoked_with}` command',
                    description=f'**Format**\n'
                    f'```{prefix}{context.invoked_with} {context.command.signature}```\n'
                    f'Creates a new or Updates an existing Daily task.\n'
                    '• `game` is one of the following: `hi3`\n'
                    '• `emoji` should be text, and I can see it, no colons please.\n'
                    '• `description` - the description of the daily task.'
                )
            elif context.invoked_with == 'rdaily':
                await context.say_as_embed(
                    title=f'How to use `{context.invoked_with}` command',
                    description=f'**Format**\n'
                    f'```{prefix}{context.invoked_with} {context.command.signature}```\n'
                    f'Removes an existing Daily task.\n'
                    '• `game` is one of the following: `hi3`\n'
                    '• `emoji` should be text, and I can see it, no colons please.'
                )


def setup(bot):
    bot.add_cog(DailyManagementCommand(bot))
