# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0009_auto_event_type_stop_usage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='id',
            new_name='sameAs',
        ),
        migrations.AlterField(
            model_name='device',
            name='sameAs',
            field=models.URLField(verbose_name='URI provided by the agent.')
        ),
    ]
