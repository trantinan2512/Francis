# Generated by Django 2.1 on 2018-08-21 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_gachainfo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gachainfo',
            old_name='jewel_owned',
            new_name='crystal_owned',
        ),
        migrations.RenameField(
            model_name='gachainfo',
            old_name='jewel_used',
            new_name='crystal_used',
        ),
    ]
