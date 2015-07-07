# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import photos.models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0004_photo_image_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='image_height',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='image_width',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='message',
            field=models.TextField(max_length=b'120', blank=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='thumbnail',
            field=models.ImageField(default=10, upload_to=photos.models.get_image_path),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='thumbnail_height',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='thumbnail_width',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
