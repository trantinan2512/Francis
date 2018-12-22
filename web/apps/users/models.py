from django.db import models
from pytz import timezone
from datetime import datetime
from django.contrib.postgres.fields import ArrayField


class DiscordUser(models.Model):
    discord_id = models.CharField(max_length=50)
    discord_name = models.CharField(max_length=200, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.discord_name} - {self.discord_id}'

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not hasattr(self, 'investigation_info'):
            InvestigationInfo.objects.create(discord_user=self)
        if not hasattr(self, 'gacha_info'):
            GachaInfo.objects.create(discord_user=self)


class InvestigationInfo(models.Model):
    discord_user = models.OneToOneField(
        DiscordUser, on_delete=models.CASCADE, blank=True, null=True, related_name='investigation_info')
    discovered_hints = ArrayField(models.PositiveIntegerField(), blank=True, null=True)

    def get_discovered_hints(self):
        if not self.discovered_hints:
            return []
        else:
            return self.discovered_hints


class GachaInfo(models.Model):
    discord_user = models.OneToOneField(DiscordUser, on_delete=models.CASCADE, blank=True, null=True, related_name='gacha_info')
    rare_item_count = models.IntegerField(default=0)
    epic_item_count = models.IntegerField(default=0)
    unique_item_count = models.IntegerField(default=0)
    legendary_item_count = models.IntegerField(default=0)
    unique_emblem_item_count = models.IntegerField(default=0)
    legendary_emblem_item_count = models.IntegerField(default=0)
    crystal_owned = models.IntegerField(default=0)
    crystal_used = models.IntegerField(default=0)
    daily_check = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.discord_user.discord_name}\'s'

    def crystal_total(self):
        return self.crystal_owned + self.crystal_used

    def daily_checked(self):
        vn_tz = timezone('Asia/Ho_Chi_Minh')
        today = datetime.now().astimezone(vn_tz)

        if self.daily_check:
            checked_time = self.daily_check.astimezone(vn_tz)

            if checked_time.date() >= today.date():
                return True
            else:
                return False
        else:
            return False
    daily_checked.boolean = True
