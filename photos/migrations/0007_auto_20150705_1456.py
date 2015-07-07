# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0006_auto_20150705_1438'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='image_cropped_height',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='image_cropped_width',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='image_height',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='image_width',
        ),
    ]
