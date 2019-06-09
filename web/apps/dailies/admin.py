from django.contrib import admin
from .models import HonkaiImpactDaily


class HonkaiImpactDailyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'emoji',
        'ordering',
        'description',
        'active',
    )
    list_editable = (
        'emoji',
        'ordering',
        'description',
        'active',
    )

    actions = (
        'reset_sent_at',
    )

    def reset_sent_at(self, request, queryset):
        queryset.update(sent_at=None)

    reset_sent_at.short_description = 'Reset Sent At'


admin.site.register(HonkaiImpactDaily, HonkaiImpactDailyAdmin)
