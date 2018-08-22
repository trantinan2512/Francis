# Generated by Django 2.1 on 2018-08-20 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemsubtype',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_types', to='jobs.Job'),
        ),
    ]
