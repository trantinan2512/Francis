import discord
import asyncio
import traceback

from textblob import TextBlob
from discord.ext import commands
import config as settings

from web.apps.investigations.models import Case


class InvestigationGameCommands:
    """Command package for Investigation Game!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='inspect', aliases=['check', 'investigate', ])
    @commands.has_role(settings.DISCORD_ROLE_FOR_INVESTIGATION)
    async def _inspect_object_command(self, context, *, sentence: str):
        active_case = Case.objects.filter(status='active').first()
        if not active_case:
            err = await context.say_as_embed(
                f'{context.author.mention}, there are no active events right now. Please check back later!', color='error')
            await err.edit(delete_after=5)
            await context.message.delete()
            return

        if not active_case.hints.filter(channel_id=context.channel.id).exists():
            err = await context.say_as_embed(
                f'{context.author.mention}, this channel does not have any objects to inspect.', color='error')
            await err.edit(delete_after=5)
            await context.message.delete()
            return

        objects = self.process_input_for_nouns(sentence)
        triggered_word = ''
        hint = None
        for obj in objects:
            hint = active_case.hints.filter(triggers__icontains=obj).first()
            if hint:
                triggered_word = obj
                break

        if not hint:
            err = await context.say_as_embed(
                f'{context.author.mention}, nothing could be yielded from your inspection. '
                'Please refer to the area description to continue the investigation.', color='error')
            await err.edit(delete_after=5)
            await context.message.delete()
            return

        triggers = hint.triggers.split(';')
        triggers_lowered = [trigger.lower() for trigger in triggers]
        if not any(obj.lower() in triggers_lowered for obj in objects):
            err = await context.say_as_embed(
                f'{context.author.mention}, nothing could be yielded from your inspection. '
                'Please refer to the area description to continue the investigation.', color='error')
            await err.edit(delete_after=5)
            await context.message.delete()
            return

        if hint.is_pinned:
            err = await context.say_as_embed(
                f'{context.author.mention}, a clue in the **{triggered_word.capitalize()}** has already been discovered! '
                'Please check pinned message.', color='warning')
            await err.edit(delete_after=5)
            await context.message.delete()
            return

        if not hint.is_clue:
            msg = await context.say_as_embed(f'{context.author.mention}, {hint.message}')
            await hint.discover_trophy(self.bot, context)
            return

        embed = discord.Embed(
            title=f'A clue has been discovered by [{context.author.display_name}]',
            description=hint.message,
            color=settings.EMBED_DEFAULT_COLOR
        )
        msg = await context.send(embed=embed)

        try:
            await msg.pin()
        except discord.Forbidden:
            await context.say_as_embed(
                'Unable to pin the clue. Insufficient permission.', color='error')
            return
        except discord.NotFound:
            await context.say_as_embed(
                'Unable to pin the clue. Message not found.', color='error')
            return
        except discord.HTTPException:
            await context.say_as_embed(
                'Unable to pin the clue. Probably due to reach channel\'s pinned messages limit (50).', color='error')
            return
        hint.is_pinned = True
        hint.save()
        await hint.discover_trophy(self.bot, context)

    def process_input_for_nouns(self, sentence):
        """
        Returns a list of unique noun/noun phrases used as a check
        for triggering words
        """
        tb = TextBlob(sentence)
        nouns = []
        for index, chunk in enumerate(tb.pos_tags):
            # check if the word is a noun
            # More info:
            # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
            if chunk[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                # forms the noun
                word = chunk[0]

                nouns.append(word)

                # initiates while loop index
                init_loop = 1
                while (
                    # check if the previous word of the noun is a Noun or an Adjective and
                    tb.pos_tags[index - init_loop][1] in ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS'] and
                    # the checking index is within the length of pos_tags
                    0 <= index - init_loop < len(tb.pos_tags)
                ):
                    # prepend the previous N/Adj to the current noun
                    word = tb.pos_tags[index - init_loop][0] + ' ' + word
                    init_loop += 1
                    # update the noun word/phrases list
                    nouns.append(word)
        objects = list(set(nouns))
        objects.sort(key=len, reverse=True)
        # return a unique list of noun/noun phrases
        return objects

    @_inspect_object_command.error
    async def _inspect_object_command_error_handler(self, context, error):
        if context.guild.id == settings.MSVN_SERVER_ID:
            return

        if isinstance(error, commands.CheckFailure):
            msg = await context.say_as_embed(
                f'{context.author.mention}, '
                f'you must have **{settings.DISCORD_ROLE_FOR_INVESTIGATION}** role to use this command!', color='error')
            await asyncio.sleep(5)
            await msg.delete()
            await context.message.delete()
            return

        if isinstance(error, commands.BadArgument):
            await context.say_as_embed(str(error), color='error')
            return

        if isinstance(error, commands.MissingRequiredArgument):
            prefix = self.bot.command_prefix
            command_name = context.invoked_with
            embed = discord.Embed(
                title=f'How to use the `{command_name}` command',
                description=''
                f'Format: ```{prefix}{command_name} [Inspected object]```\n'
                f'Inspects an object. Objects are described in the context of the message in that channel.\n'
                f'__Example:__\n`{prefix}{command_name} trash can` '
                '- Inspects the **trash can** given that the context of the message has a [trash can].',
                color=settings.EMBED_DEFAULT_COLOR
            )
            await context.send(embed=embed)
            return

        if settings.DEBUG:
            await context.send(f'```bash\n{traceback.format_exc()}```')


def setup(bot):
    bot.add_cog(InvestigationGameCommands(bot))