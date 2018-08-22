from django.db import models
try:
    from apps.items.models import ItemRank, Item
    from apps.jobs.models import Job
except ModuleNotFoundError:
    from web.apps.items.models import ItemRank, Item
    from web.apps.jobs.models import Job

# Create your models here.


class TreasureBoxGacha(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='treasure_box_gachas')
    rank = models.ForeignKey(ItemRank, on_delete=models.CASCADE, related_name='treasure_box_gachas')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='treasure_box_gachas')
    rate = models.FloatField(default=0.0)
