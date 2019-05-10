from django.db import models
import discord

class HonkaiImpactDaily(models.Model):
    hi_dailies_channel_id = 574908075933433866

    class Meta:
        verbose_name = 'Honkai Impact Daily'
        verbose_name_plural = 'Honkai Impact Dailies'

    emoji = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=1000)
    active = models.BooleanField(default=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    message_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.description[:30]}...'

    def parse_emoji(self, bot):
        parsed_emoji = discord.utils.get(bot.emojis, name=self.emoji)
        if parsed_emoji:
            return parsed_emoji
        try:
            emoji = int(self.emoji)
            parsed_emoji = f'{emoji}\u20E3' if emoji in list(range(0, 10)) else str(emoji)
        except ValueError:
            pass

        return parsed_emoji

    async def fetch_message(self, bot):
        channel = bot.get_channel(self.hi_dailies_channel_id)
        if not channel:
            return None

        try:
            message = await channel.fetch_message(self.message_id)
        except Exception:
            return None

        return message
