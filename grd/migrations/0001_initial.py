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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('id', models.CharField(max_length=128, verbose_name='Identifier provided by the agent.')),
                ('hid', models.CharField(max_length=32, verbose_name='Hardware identifier.')),
                ('type', models.CharField(max_length=16, choices=[('computer', 'computer'), ('mobile', 'mobile'), ('monitor', 'monitor'), ('peripheral', 'peripheral')])),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(max_length=16, choices=[('register', 'REGISTER'), ('recycle', 'RECYCLE')])),
                ('data', models.TextField()),
                ('event_time', models.DateTimeField(verbose_name='Time when the event has happened.')),
                ('by_user', models.CharField(max_length=32, verbose_name='User who performs the event.')),
                ('agent', models.ForeignKey(to='grd.Agent', related_name='+')),
                ('components', models.ManyToManyField(to='grd.Device', related_name='parent_logs')),
                ('device', models.ForeignKey(to='grd.Device', related_name='logs')),
            ],
            options={
                'get_latest_by': 'timestamp',
            },
        ),
    ]
