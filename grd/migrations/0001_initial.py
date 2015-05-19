# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('email', models.EmailField(unique=True, verbose_name='email address', max_length=255)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('is_admin', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('uuid', models.UUIDField(editable=False, serialize=False, primary_key=True, default=uuid.uuid4)),
                ('id', models.CharField(verbose_name='Identifier provided by the agent.', max_length=128)),
                ('hid', models.CharField(verbose_name='Hardware identifier.', max_length=32)),
                ('type', models.CharField(choices=[('computer', 'computer'), ('mobile', 'mobile'), ('monitor', 'monitor'), ('peripheral', 'peripheral')], max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='EntryLog',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(choices=[('register', 'REGISTER'), ('recycle', 'RECYCLE')], max_length=16)),
                ('data', models.TextField()),
                ('event_time', models.DateTimeField(verbose_name='Time when the event has happened.')),
                ('by_user', models.CharField(verbose_name='User who performs the event.', max_length=32)),
                ('agent', models.ForeignKey(to='grd.Agent', related_name='+')),
                ('components', models.ManyToManyField(to='grd.Device', related_name='parent_logs')),
                ('device', models.ForeignKey(to='grd.Device', related_name='logs')),
            ],
            options={
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='agent',
            field=models.ForeignKey(related_name='users', null=True, to='grd.Agent'),
        ),
    ]
