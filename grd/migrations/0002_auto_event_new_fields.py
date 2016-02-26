# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['grdDate'], 'get_latest_by': 'grdDate'},
        ),
        migrations.RenameField(
            model_name='event',
            old_name='grdTimestamp',
            new_name='grdDate',
        ),
        migrations.AddField(
            model_name='event',
            name='dhDate',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 23, 9, 9, 52, 392029, tzinfo=utc), verbose_name='Time when the event has happened.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='errors',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='geo',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='event',
            name='incidence',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='secured',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='byUser',
            field=models.URLField(verbose_name='User who performs the event.'),
        ),
    ]
