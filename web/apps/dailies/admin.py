from django.contrib import admin
from .models import HonkaiImpactDaily


class HonkaiImpactDailyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'emoji',
        'description',
        'active',
    )
    list_editable = (
        'emoji',
        'description',
        'active',
    )


admin.site.register(HonkaiImpactDaily, HonkaiImpactDailyAdmin)
