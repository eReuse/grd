# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0002_auto_increase_by_user_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='type',
            field=models.CharField(max_length=16, choices=[('computer', 'computer'), ('laptop', 'laptop'), ('mobile', 'mobile'), ('monitor', 'monitor'), ('peripheral', 'peripheral')]),
        ),
    ]
