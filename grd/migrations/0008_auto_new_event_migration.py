# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0007_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(
                max_length=16,
                choices=[
                    ('register', 'REGISTER'),
                    ('collect', 'COLLECT'),
                    ('recycle', 'RECYCLE'),
                    ('add', 'ADD'),
                    ('remove', 'REMOVE'),
                    ('migrate', 'MIGRATE')
                ]
            ),
        ),
    ]
