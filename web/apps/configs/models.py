from django.db import models


class TrophyRoomConfig(models.Model):

    class Meta:
        verbose_name = 'Trophy Room Config'
        verbose_name_plural = verbose_name

    room_channel_id = models.BigIntegerField(
        help_text='Put ID of the channel to display trophy list here.')
    trophy_list_message_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Trophy Room Config'

    def get_trophy_room(self, context):
        return context.guild.get_channel(self.room_channel_id)

    async def get_trophy_list_message(self, context):
        channel = self.get_trophy_room(context)
        if channel and self.trophy_list_message_id:
            try:
                message = await channel.fetch_message(self.trophy_list_message_id)
            except Exception:
                return None
            return message
        return None
