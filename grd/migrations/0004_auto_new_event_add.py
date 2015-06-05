# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0003_auto_rename_log__event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('register', 'REGISTER'), ('collect', 'COLLECT'), ('recycle', 'RECYCLE'), ('add', 'ADD')], max_length=16),
        ),
    ]
