# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0007_auto_update_event_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentUser',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID',
                    auto_created=True,
                    serialize=False,
                    primary_key=True)
                ),
                ('url', models.URLField(
                    verbose_name='URL pointing to an User or an Organization.',
                    max_length=128,
                    unique=True)
                ),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(to='grd.AgentUser', null=True),
        ),
    ]
