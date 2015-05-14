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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length='128', unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('id', models.CharField(verbose_name='Identifier provided by the agent.', max_length=128)),
                ('hid', models.CharField(verbose_name='Hardware identifier.', max_length=32)),
                ('type', models.CharField(choices=[('computer', 'computer'), ('mobile', 'mobile'), ('monitor', 'monitor'), ('peripheral', 'peripheral')], max_length='16')),
            ],
        ),
        migrations.CreateModel(
            name='EntryLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(choices=[('register', 'REGISTER'), ('recycle', 'RECYCLE')], max_length='16')),
                ('data', models.TextField()),
                ('event_time', models.DateTimeField(verbose_name='Time when the event has happened.')),
                ('by_user', models.CharField(verbose_name='User who performs the event.', max_length='32')),
                ('agent', models.ForeignKey(to='grd.Agent', related_name='+')),
                ('components', models.ManyToManyField(to='grd.Device', related_name='parent_logs')),
                ('device', models.ForeignKey(to='grd.Device', related_name='logs')),
            ],
        ),
    ]
