# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length='128')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EntryLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(max_length='16', choices=[('register', 'REGISTER'), ('use', 'USE'), ('transfer', 'TRANSFER'), ('collect', 'COLLECT'), ('recycle', 'RECYCLE')])),
                ('data', models.TextField()),
                ('agent', models.ForeignKey(to='grd.Agent', related_name='logs')),
                ('device', models.ForeignKey(to='grd.Device', related_name='logs')),
            ],
        ),
    ]
