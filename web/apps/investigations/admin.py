from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django import forms
from django.utils.html import format_html
from .models import Case, Hint


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        exclude = []

    def clean(self):
        if 'status' in self.changed_data:
            if self.cleaned_data['status'] == 'active':
                active_cases = Case.objects.filter(status='active')
                if active_cases.exists():
                    err_msg = format_html(
                        'You can only have 1 Active case at a time! <br/>'
                        f'Currently active case: <strong><a href="/admin/investigations/case/'
                        f'{active_cases.first().id}/change/" target="_blank">{active_cases.first().name} (Edit)</a></strong>.')
                    self.add_error('status', err_msg)
        super().clean()


class CaseAdmin(admin.ModelAdmin):

    form = CaseForm

    list_display = (
        'id',
        'name',
        'short_description',
        'status',
        'created_at',
        'closed_at',
    )

    list_editable = (
        # 'status',
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'id',
        'name',
        'description',
    )

    def get_changelist_form(self, request, **kwargs):
        return self.form

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     if not self.has_view_or_change_permission(request):
    #         queryset = queryset.none()
    #     if
    #     return queryset


class HintAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.TextField: {'widget': Textarea(
            attrs={'rows': 3,
                   'cols': 40,
                   'style': 'height: 7em;'})},
        models.CharField: {'widget': TextInput(
            attrs={'style': 'width: 200px;'})},
    }

    list_display = (
        'id',
        'case',
        'name',
        'channel_id',
        'triggers',
        'message',
        'is_clue',
        'is_pinned',
        'required_hints',
    )

    list_editable = (
        'case',
        'channel_id',
        'triggers',
        'message',
        'is_clue',
        'is_pinned',
        'required_hints',
    )

    list_filter = (
        'is_clue',
        'is_pinned',
        'case',
    )

    search_fields = (
        'case__name',
        'case__id',
        'channel_id',
        'triggers',
    )


admin.site.register(Case, CaseAdmin)
admin.site.register(Hint, HintAdmin)
