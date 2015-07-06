# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=128)),
                ('description', models.TextField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.CharField(verbose_name='Identifier provided by the agent.', max_length=128)),
                ('hid', models.CharField(serialize=False, primary_key=True, verbose_name='Hardware identifier.', max_length=128)),
                ('type', models.CharField(choices=[('computer', 'computer'), ('mobile', 'mobile'), ('monitor', 'monitor'), ('peripheral', 'peripheral')], max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('register', 'REGISTER'), ('collect', 'COLLECT'), ('recycle', 'RECYCLE'), ('add', 'ADD'), ('remove', 'REMOVE'), ('migrate', 'MIGRATE')], max_length=16)),
                ('data', django.contrib.postgres.fields.hstore.HStoreField(default={})),
                ('event_time', models.DateTimeField(verbose_name='Time when the event has happened.')),
                ('by_user', models.CharField(verbose_name='User who performs the event.', max_length=32)),
            ],
            options={
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('label', models.CharField(max_length=50)),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('event', models.OneToOneField(serialize=False, to='grd.Event', primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='agent',
            field=models.ForeignKey(to='grd.Agent', related_name='+'),
        ),
        migrations.AddField(
            model_name='event',
            name='components',
            field=models.ManyToManyField(to='grd.Device', related_name='parent_events'),
        ),
        migrations.AddField(
            model_name='event',
            name='device',
            field=models.ForeignKey(to='grd.Device', related_name='events'),
        ),
    ]
