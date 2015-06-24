# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.operations import HStoreExtension
from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0005_auto_new_event_remove'),
    ]

    operations = [
        HStoreExtension(),
        migrations.RemoveField(
            model_name='event',
            name='data',
        ),
        migrations.AddField(
            model_name='event',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}),
        ),
    ]
