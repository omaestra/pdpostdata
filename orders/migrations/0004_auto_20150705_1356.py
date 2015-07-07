# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20150605_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrating',
            name='rate',
            field=models.DecimalField(max_digits=1, decimal_places=0, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]),
        ),
    ]
