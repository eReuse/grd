# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0005_auto_types_as_camelcase'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={
                'ordering': ['grdTimestamp'],
                'get_latest_by': 'grdTimestamp'
            },
        ),
        migrations.RenameField(
            model_name='event',
            old_name='by_user',
            new_name='byUser',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='event_time',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='timestamp',
            new_name='grdTimestamp',
        ),
    ]
