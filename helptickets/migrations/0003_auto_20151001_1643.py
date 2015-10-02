# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helptickets', '0002_auto_20150930_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpticket',
            name='help_ticket_id',
            field=models.CharField(default=b'ABC', unique=True, max_length=120),
        ),
        migrations.AddField(
            model_name='helpticket',
            name='status',
            field=models.CharField(default=b'Abierto', max_length=120, choices=[(b'Abierto', b'Abierto'), (b'Cerrado', b'Cerrado')]),
        ),
    ]
