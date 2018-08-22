from django.contrib import admin
from .models import TreasureBoxGacha
# Register your models here.


class TreasureBoxGachaAdmin(admin.ModelAdmin):
    list_display = (
        'job',
        'rank',
        'item',
        'rate'
    )


admin.site.register(TreasureBoxGacha, TreasureBoxGachaAdmin)
