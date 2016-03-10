# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grd', '0003_auto_event_date_is_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='type',
            field=models.CharField(max_length=16, choices=[('Computer', 'computer'), ('Mobile', 'mobile'), ('Monitor', 'monitor'), ('Peripheral', 'peripheral'), ('GraphicCard', 'GraphicCard'), ('HardDrive', 'HardDrive'), ('Motherboard', 'Motherboard'), ('NetworkAdapter', 'NetworkAdapter'), ('OpticalDrive', 'OpticalDrive'), ('Processor', 'Processor'), ('RamModule', 'RamModule'), ('SoundCard', 'SoundCard')]),
        ),
    ]
