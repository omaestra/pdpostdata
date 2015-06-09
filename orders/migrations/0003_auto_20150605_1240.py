# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20150605_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrating',
            name='order',
            field=models.OneToOneField(to='orders.Order'),
        ),
    ]
