from django import forms
from django.contrib import admin
from .models import TrophyRoomConfig


class TrophyRoomConfigForm(forms.ModelForm):
    class Meta:
        model = TrophyRoomConfig
        exclude = ['trophy_list_message_id', ]

    def clean(self):
        if not self.instance.id:
            if TrophyRoomConfig.objects.count() >= 1:
                self.add_error(None, 'You can only have 1 Trophy Room Configuration!')
        super().clean()


class TrophyRoomConfigAdmin(admin.ModelAdmin):

    form = TrophyRoomConfigForm

    list_display = (
        '__str__',
        'room_channel_id',
        'trophy_list_message_id',
        'created_at',
        'updated_at',
    )

    list_editable = (
        'room_channel_id',
    )


admin.site.register(TrophyRoomConfig, TrophyRoomConfigAdmin)
