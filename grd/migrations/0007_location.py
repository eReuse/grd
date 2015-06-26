# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0006_auto_data_pg_hstorefield'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('label', models.CharField(max_length=50)),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('event', models.OneToOneField(primary_key=True, serialize=False, to='grd.Event')),
            ],
        ),
    ]
