from django.db import models
try:
    from apps.jobs.models import Job
except ModuleNotFoundError:
    from web.apps.jobs.models import Job
# Create your models here.


class ItemType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return str(self.type)


class ItemSubType(models.Model):
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='sub_types')
    sub_type = models.CharField(max_length=50)

    def __str__(self):
        return str(self.sub_type)


class ItemRank(models.Model):
    rank = models.CharField(max_length=50)
    max_star = models.IntegerField(default=5)
    max_level = models.IntegerField(default=5)
    emblem_rate = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.rank)


class ItemStat(models.Model):
    stat = models.CharField(max_length=100)

    def __str__(self):
        return str(self.stat)


class ItemStatRange(models.Model):
    stat = models.ForeignKey(ItemStat, on_delete=models.CASCADE, related_name='stat_range')
    rank = models.ForeignKey(ItemRank, on_delete=models.CASCADE, related_name='stat_range')
    sub_type = models.ForeignKey(ItemSubType, on_delete=models.CASCADE, related_name='stat_range')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='stat_range', blank=True, null=True)
    job_specific = models.BooleanField(default=True)
    emblem = models.BooleanField(default=False)
    min = models.FloatField(default=0.0)
    max = models.FloatField(default=0.0)
    base = models.FloatField(default=0.0)
    fixed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.rank} {self.sub_type} - {self.stat}'


class Item(models.Model):
    name = models.CharField(max_length=200)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    sub_type = models.ForeignKey(ItemSubType, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    stats = models.ManyToManyField(ItemStat, related_name='items', blank=True)

    def __str__(self):
        return str(self.name)
