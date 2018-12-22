from django.contrib import admin
from django.db import models
from django.forms import TextInput
from .models import Chapter, Trophy


class ChapterAdmin(admin.ModelAdmin):
    ordering = (
        'chapter',
    )
    list_display = (
        '__str__',
        'chapter',
        'name',
        'emoji',
        'is_active',
    )

    list_editable = (
        'chapter',
        'name',
        'emoji',
        'is_active',
    )


class TrophyAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.CharField: {'widget': TextInput(
            attrs={'style': 'width: 200px;'})},
    }

    list_display = (
        '__str__',
        'chapter',
        'name',
        'position',
        'emoji',
        'hint',
        '_discovered',
        'discovered_by',
        'discovered_at',
    )

    list_editable = (
        'chapter',
        'name',
        'position',
        'emoji',
        'hint',
    )

    list_filter = (
        'chapter',
    )


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Trophy, TrophyAdmin)
