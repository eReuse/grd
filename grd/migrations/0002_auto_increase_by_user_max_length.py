# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='by_user',
            field=models.CharField(verbose_name='User who performs the event.',
                                   max_length=128),
        ),
    ]
