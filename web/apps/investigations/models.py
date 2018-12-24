import discord
from django.conf import settings
from django.db import models
from django.utils import timezone
from utils.user import get_user_obj
from web.apps.configs.models import TrophyRoomConfig
from django.contrib.postgres.fields import JSONField, ArrayField


class Case(models.Model):
    CASE_STATUSES = (
        ('unknown', 'Unknown'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('failed', 'Failed'),
    )

    name = models.CharField(
        help_text='Give your case a cool name! For management purposes.',
        max_length=200)
    description = models.TextField(
        help_text='Optional. For management purposes, too.',
        max_length=2000, blank=True)
    status = models.CharField(
        help_text='Optional. This will change depending on the scenarios.<br/>'
        '• <strong>Unknown</strong> is the default status. Mark it as <strong>Active</strong> after you set the clues, '
        'then all the Clues are available to be discovered.<br/>'
        '• Mark as <strong>Active</strong> when you want to activate the case. '
        '<strong>Only 1 Active case at a time.</strong><br/>'
        '• Mark as <strong>Closed</strong> when the case is complete.<br/>'
        '• Mark as <strong>Failed</strong> when the case is not solved.',
        max_length=50, default='unknown', choices=CASE_STATUSES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.status == 'closed':
            self.closed_at = timezone.now()
        else:
            self.closed_at = None
        super().save(*args, **kwargs)

    @property
    def short_description(self):
        if self.description:
            return f'{self.description[:100]}...'


class Hint(models.Model):
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, related_name='hints',
        help_text='Select one of the Cases or click that + button to create one.',)
    name = models.CharField(
        help_text='Optional, give it a name to easier distinguish with other clues.',
        max_length=200, blank=True)
    channel_id = models.BigIntegerField(
        help_text='The channel ID the clues are in. Enable Discord Developer Mode and right-click on the channel to Copy ID.')
    triggers = models.CharField(
        help_text='A list of trigger words separated by semicolons (;). Eg: trash;trash can;recycle bin',
        max_length=200)
    message = models.TextField(
        help_text='Discord markdown enabled.<br/>'
        '• To mention someone, use <@user_id>.<br/>'
        '• To mention a role, use <@&role_id>.<br/>'
        '• To mention a channel, use <#channel_id>.',
        max_length=2000)
    is_clue = models.BooleanField(
        help_text='Check this to make this a Clue, otherwise it\'s just a normal message with no clues in it.',
        default=False)
    is_pinned = models.BooleanField(
        help_text='A pinned clue is one that has been discovered.',
        default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    pinned_at = models.DateTimeField(blank=True, null=True, editable=False)

    actions = JSONField(blank=True, null=True)

    required_hints = ArrayField(models.PositiveIntegerField(), blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return f'Clue {self.id}'

    def save(self, *args, **kwargs):
        if self.is_pinned is True:
            self.pinned_at = timezone.now()
        super().save(*args, **kwargs)

    def get_required_hints(self):
        if not self.required_hints:
            return []
        else:
            return self.required_hints

    async def discover_trophy(self, bot, context):
        if not hasattr(self, 'trophy'):
            return
        if self.trophy.discovered or not self.trophy.chapter.is_active:
            return

        await context.say_as_embed(
            f'{context.author.mention}, you found {self.trophy.get_emoji(bot)} '
            f'**{self.trophy.name}** trophy here! Congrats!')
        self.trophy.discovered_by = get_user_obj(context.author)
        self.trophy.discovered_at = timezone.now()
        self.trophy.save()

        trophy_room_config = TrophyRoomConfig.objects.first()
        if not trophy_room_config:
            await context.say_as_embed(
                'Trophy Room not configured, please contact an admin regarding this error.', color='error')
            return

        channel = trophy_room_config.get_trophy_room(context)
        if not channel:
            await context.say_as_embed(
                'Trophy Room **Channel** improperly configured, please contact an addmin regarding this error.',
                color='error')
            return

        message = await trophy_room_config.get_trophy_list_message(context)
        if message:
            try:
                await message.delete()
            except Exception:
                await context.say_as_embed(
                    'Unable to delete outdated trophy list message, please contact an addmin regarding this error.',
                    color='error')

        await channel.send(
            f'{context.author.mention} found {self.trophy.get_emoji(bot)} '
            f'**{self.trophy.name}** trophy! Congrats!!')

        try:
            active_chapters = Chapter.objects.filter(is_active=True).order_by('chapter')
        except NameError:
            from db.apps.chapters.models import Chapter
            active_chapters = Chapter.objects.filter(is_active=True).order_by('chapter')

        if not active_chapters.exists():
            return

        msg = ''
        for chapter in active_chapters:
            if not chapter.trophies.exists():
                continue
            trophy_emojis = [
                trophy.get_emoji(bot) if trophy.discovered else '❌' for trophy in chapter.trophies.order_by('position')
            ]
            msg += f'{" ".join(trophy_emojis)} - **{chapter.name}** {chapter.get_emoji(bot)}\n'

        embed = discord.Embed(
            title='Trophy List',
            description=msg,
            color=settings.EMBED_DEFAULT_COLOR
        )
        msg = await channel.send(embed=embed)
        trophy_room_config.trophy_list_message_id = msg.id
        trophy_room_config.save()

    async def act(self, bot, context):
        if self.actions:
            if 'channel_access' in self.actions:
                channel = bot.get_channel(self.actions['channel_access'])
                if not channel:
                    await context.say_as_embed('Channel not found.', color='error')
                    return
                await channel.set_permissions(context.author, read_messages=True, send_messages=True)
                msg = await context.say_as_embed(
                    f'{context.author.mention}, {channel.mention} unlocked! You can now access it.')
                await msg.edit(delete_after=7)
