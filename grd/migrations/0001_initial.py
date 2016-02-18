# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField()),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgentUser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('url', models.URLField(max_length=128, verbose_name='URL pointing to an User or an Organization.', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('sameAs', models.URLField(verbose_name='URI provided by the agent.', unique=True)),
                ('hid', models.CharField(max_length=128, verbose_name='Hardware identifier.', validators=[django.core.validators.RegexValidator(regex='\\w+-\\w+-\\w+')], null=True, unique=True)),
                ('type', models.CharField(choices=[('Computer', 'computer'), ('Laptop', 'laptop'), ('Mobile', 'mobile'), ('Monitor', 'monitor'), ('Peripheral', 'peripheral')], max_length=16)),
                ('productionDate', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.CharField(choices=[('Add', 'ADD'), ('Allocate', 'ALLOCATE'), ('Deallocate', 'DEALLOCATE'), ('Locate', 'LOCATE'), ('Migrate', 'MIGRATE'), ('Register', 'REGISTER'), ('Receive', 'RECEIVE'), ('Recycle', 'RECYCLE'), ('Remove', 'REMOVE'), ('StopUsage', 'STOPUSAGE'), ('UsageProof', 'USAGEPROOF')], max_length=16)),
                ('date', models.DateTimeField(verbose_name='Time when the event has happened.')),
                ('grdTimestamp', models.DateTimeField(auto_now_add=True)),
                ('byUser', models.CharField(max_length=128, verbose_name='User who performs the event.')),
                ('data', django.contrib.postgres.fields.hstore.HStoreField(default={})),
            ],
            options={
                'get_latest_by': 'grdTimestamp',
                'ordering': ['grdTimestamp'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('event', models.OneToOneField(primary_key=True, serialize=False, to='grd.Event')),
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
            field=models.ManyToManyField(related_name='parent_events', to='grd.Device'),
        ),
        migrations.AddField(
            model_name='event',
            name='device',
            field=models.ForeignKey(to='grd.Device', related_name='events'),
        ),
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(to='grd.AgentUser', null=True),
        ),
    ]
