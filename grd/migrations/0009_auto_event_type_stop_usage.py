# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0008_auto_add_event_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(
                choices=[
                    ('Add', 'ADD'),
                    ('Allocate', 'ALLOCATE'),
                    ('Deallocate', 'DEALLOCATE'),
                    ('Locate', 'LOCATE'),
                    ('Migrate', 'MIGRATE'),
                    ('Register', 'REGISTER'),
                    ('Receive', 'RECEIVE'),
                    ('Recycle', 'RECYCLE'),
                    ('Remove', 'REMOVE'),
                    ('StopUsage', 'STOPUSAGE'),
                    ('UsageProof', 'USAGEPROOF')
                ],
                max_length=16
            ),
        ),
    ]
