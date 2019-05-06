import asyncio
import discord
from django.utils import timezone
from datetime import datetime
from utils.time import process_elapsed_time_text

from web.apps.dailies.models import HonkaiImpactDaily


class Dailies:

    def __init__(self, bot):
        self.bot = bot
        self.hi_dailies = HonkaiImpactDaily.objects.filter(active=True)

        self.hi_dailies_channel_id = 574908075933433866

    async def honkai_impact(self):
        print('[HI3rd Dailies Reset] Waiting for ready state...')

        await self.bot.wait_until_ready()

        self.hi_dailies_channel = self.bot.get_channel(self.hi_dailies_channel_id)

        print('[HI3rd Dailies Reset] Ready and running!')

        while not self.bot.is_closed():
            await asyncio.sleep(10)

            if not self.hi_dailies_channel:
                print(f'Channel with ID [ {self.hi_dailies_channel_id} ] does not exist.')
                return

            self.hi_dailies = HonkaiImpactDaily.objects.filter(active=True).order_by('emoji')

            if not self.hi_dailies.exists():
                continue

            await self.update_time_til_reset()

            if self.next_reset and timezone.now() < self.next_reset:
                continue

            try:
                msg = await self.hi_dailies_channel.fetch_message(self.hi_dailies.first().message_id)
                await msg.delete()
            except discord.HTTPException:
                pass

            embed = discord.Embed(
                title='Dailies Checker',
                description=self.til_next_reset,
                color=discord.Color.dark_blue(),
                timestamp=timezone.now()
            )

            embed.add_field(
                name='React to mark it as Done',
                value=self.dailies_txt
            )

            message = await self.hi_dailies_channel.send(embed=embed)

            for e in self.emojis:
                await message.add_reaction(e)

            self.hi_dailies.update(sent_at=timezone.now())
            self.hi_dailies.update(message_id=message.id)

    def parse_emoji(self, emoji):
        parsed_emoji = discord.utils.get(self.bot.emojis, name=emoji)
        if parsed_emoji:
            return parsed_emoji
        try:
            emoji = int(emoji)
            parsed_emoji = f'{emoji}\u20E3' if emoji in list(range(0, 10)) else emoji
        except ValueError:
            pass

        return parsed_emoji

    @property
    def emojis(self):
        emojis = []
        if not self.hi_dailies.exists():
            return emojis

        for daily in self.hi_dailies:
            emoji = self.parse_emoji(daily.emoji)
            emojis.append(emoji)

        return emojis

    @property
    def dailies_txt(self):

        if not self.hi_dailies.exists():
            return None

        txt = ''
        for daily in self.hi_dailies:
            txt += f'{self.parse_emoji(daily.emoji)} - {daily.description}\n'

        return txt

    @property
    def sent_at(self):
        return self.hi_dailies.first().sent_at

    @property
    def next_reset(self):
        if self.sent_at:
            return datetime(self.sent_at.year, self.sent_at.month, self.sent_at.day + 1, 9, tzinfo=self.sent_at.tzinfo)
        else:
            return None

    async def update_time_til_reset(self):
        try:
            msg = await self.hi_dailies_channel.fetch_message(self.hi_dailies.first().message_id)
            embed = msg.embeds[0]
            embed.description = self.til_next_reset
            embed.clear_fields()
            embed.add_field(
                name='React to mark it as Done',
                value=self.dailies_txt
            )
            await msg.edit(embed=embed)
        except discord.HTTPException:
            pass

    @property
    def til_next_reset(self):
        if self.next_reset:
            return f'Daily resets in: {process_elapsed_time_text(self.next_reset - timezone.now())}'
        else:
            return 'Daily resets in: N/A'
