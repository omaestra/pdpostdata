# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import photos.models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_auto_20150705_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='image_field',
            field=models.ImageField(default=datetime.datetime(2015, 7, 5, 14, 1, 8, 214300), upload_to=photos.models.get_image_path),
            preserve_default=False,
        ),
    ]
