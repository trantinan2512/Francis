from django.contrib import admin
from .models import DiscordUser, GachaInfo
# Register your models here.


class GachaInfoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'rare_item_count',
        'epic_item_count',
        'unique_item_count',
        'legendary_item_count',
        'unique_emblem_item_count',
        'legendary_emblem_item_count',
        'crystal_owned',
        'crystal_used',
        'daily_checked'
    )


admin.site.register(DiscordUser)
admin.site.register(GachaInfo, GachaInfoAdmin)
