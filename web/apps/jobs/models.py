from django.db import models
# Create your models here.


class JobBranch(models.Model):
    branch = models.CharField(max_length=50)


class Job(models.Model):
    job = models.CharField(max_length=50)
    branch = models.ForeignKey(JobBranch, on_delete=models.CASCADE, related_name='jobs', blank=True, null=True)

    def __str__(self):
        return self.job
