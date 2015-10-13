# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0010_auto_rename__device__id__sameas'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='productionDate',
            field=models.DateField(null=True),
        ),
    ]
