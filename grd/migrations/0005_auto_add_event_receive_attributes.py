# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0004_auto_update_device_type_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='receiver',
            field=models.URLField(null=True, verbose_name='User who receives the device.'),
        ),
        migrations.AddField(
            model_name='event',
            name='receiverType',
            field=models.CharField(null=True, choices=[('FinalUser', 'Final User'), ('CollectionPoint', 'Collection Point'), ('RecyclingPoint', 'Recycling Point')], max_length=16),
        ),
    ]
