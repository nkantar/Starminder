# Generated by Django 5.1.5 on 2025-02-09 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_userprofile_day_remove_userprofile_hour'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='day',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='hour',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
