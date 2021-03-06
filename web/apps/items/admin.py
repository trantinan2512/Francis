from django.contrib import admin

from .models import ItemRank, ItemType, ItemSubType, ItemStat, ItemStatRange, Item
# Register your models here.


class ItemStatRangeAdmin(admin.ModelAdmin):
    list_display = (
        'sub_type',
        'stat',
        'job',
        'job_specific',
        'rank',
        'emblem',
        'base',
        'min',
        'max'
    )

    list_editable = (
        'base',
        'min',
        'max',
    )

    search_fields = (
        'sub_type__sub_type',
    )


admin.site.register(ItemRank)
admin.site.register(ItemType)
admin.site.register(ItemSubType)
admin.site.register(ItemStat)
admin.site.register(ItemStatRange, ItemStatRangeAdmin)
admin.site.register(Item)
