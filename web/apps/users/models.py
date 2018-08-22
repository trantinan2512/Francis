from django.db import models
from datetime import date
# Create your models here.


class DiscordUser(models.Model):
    discord_id = models.CharField(max_length=50)
    discord_name = models.CharField(max_length=200, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.discord_name} - {self.discord_id}'


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

    def crystal_total(self):
        return self.crystal_owned + self.crystal_used

    def daily_checked(self):
        today = date.today()
        checked_time = self.daily_check

        if checked_time and checked_time.date() >= today:
            return True
        else:
            return False
