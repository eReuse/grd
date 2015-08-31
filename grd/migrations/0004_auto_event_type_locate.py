# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0003_auto_device_type_laptop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('register', 'REGISTER'), ('collect', 'COLLECT'), ('recycle', 'RECYCLE'), ('add', 'ADD'), ('remove', 'REMOVE'), ('migrate', 'MIGRATE'), ('locate', 'LOCATE')], max_length=16),
        ),
    ]
