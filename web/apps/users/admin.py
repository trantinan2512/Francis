from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import DiscordUser, GachaInfo

admin.site.unregister(User)
admin.site.unregister(Group)


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

admin.site.site_header = 'Francis Discord Bot Admin Panel'
admin.site.site_title = admin.site.site_header
