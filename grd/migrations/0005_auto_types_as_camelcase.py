# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0004_auto_event_type_locate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='type',
            field=models.CharField(
                choices=[
                    ('Computer', 'computer'),
                    ('Laptop', 'laptop'),
                    ('Mobile', 'mobile'),
                    ('Monitor', 'monitor'),
                    ('Peripheral', 'peripheral')
                ],
                max_length=16
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(
                choices=[
                    ('Register', 'REGISTER'),
                    ('Collect', 'COLLECT'),
                    ('Recycle', 'RECYCLE'),
                    ('Add', 'ADD'),
                    ('Remove', 'REMOVE'),
                    ('Migrate', 'MIGRATE'),
                    ('Locate', 'LOCATE')
                ],
                max_length=16
            ),
        ),
    ]
