# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length='128')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('uuid', models.UUIDField(editable=False, serialize=False, primary_key=True, default=uuid.uuid4)),
                ('id', models.CharField(verbose_name='Device identifier provided by the agent.', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='EntryLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(choices=[('register', 'REGISTER'), ('recycle', 'RECYCLE')], max_length='16')),
                ('data', models.TextField()),
                ('agent', models.ForeignKey(to='grd.Agent', related_name='logs')),
                ('device', models.ForeignKey(to='grd.Device', related_name='logs')),
            ],
        ),
    ]
