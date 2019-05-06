from django.db import models


class HonkaiImpactDaily(models.Model):
    class Meta:
        verbose_name = 'Honkai Impact Daily'
        verbose_name_plural = 'Honkai Impact Dailies'

    emoji = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=1000)
    active = models.BooleanField(default=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    message_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.description[:30]}...'
