import discord
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from web.apps.users.models import DiscordUser
from web.apps.investigations.models import Hint

emoji_validator = RegexValidator(
    regex='^:\w{2,}:$',
    message='Please enter an emoji like :this:')


class Chapter(models.Model):
    chapter = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        help_text='Chapter number. Equal to or Greater than 1.')
    name = models.CharField(
        max_length=200,
        help_text='It is good to give it a cool name!')
    emoji = models.CharField(
        max_length=100, blank=True, validators=[emoji_validator, ],
        help_text='The emoji to display on Discord. Must looks like <strong>:this:</strong>')

    is_active = models.BooleanField(
        default=True,
        help_text='Check this to make the chapter available for users to discover trophies in it!')

    def __str__(self):
        return f'Chapter {self.chapter} - {self.name}'

    def get_emoji(self, bot):
        emoji = discord.utils.get(bot.emojis, name=self.emoji.strip(':'))
        if emoji:
            return str(emoji)
        else:
            return ''


class Trophy(models.Model):
    class Meta:
        verbose_name = 'Trophy'
        verbose_name_plural = 'Trophies'

    name = models.CharField(
        max_length=200,
        help_text='Yes, I need a name for management purposes.')
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name='trophies',
        help_text='The chapter this trophy belongs to.')
    position = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        help_text='The position of this trophy to be displayed on Discord.')
    emoji = models.CharField(
        validators=[emoji_validator, ],
        max_length=100, blank=True,
        help_text='The emoji to display on Discord. Must looks like <strong>:this:</strong>.')
    hint = models.OneToOneField(
        Hint, on_delete=models.CASCADE, related_name='trophy',
        help_text='The hint this trophy is hiding.')
    discovered_by = models.ForeignKey(
        DiscordUser, on_delete=models.SET_NULL, related_name='trophies',
        blank=True, null=True,
        help_text='The user who discovered this trophy.')
    discovered_at = models.DateTimeField(
        blank=True, null=True,
        help_text='The time when this trophy is discovered.')

    def __str__(self):
        return self.name

    def _discovered(self):
        if self.discovered_by:
            return True
        return False
    _discovered.boolean = True
    discovered = property(_discovered)

    def get_emoji(self, bot):
        emoji = discord.utils.get(bot.emojis, name=self.emoji.strip(':'))
        if emoji:
            return str(emoji)
        else:
            return ''
