# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0002_rename_event_field__event__type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='components',
            field=models.ManyToManyField(related_name='parent_events', to='grd.Device'),
        ),
        migrations.AlterField(
            model_name='event',
            name='device',
            field=models.ForeignKey(to='grd.Device', related_name='events'),
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('register', 'REGISTER'), ('collect', 'COLLECT'), ('recycle', 'RECYCLE')], max_length=16),
        ),
    ]
