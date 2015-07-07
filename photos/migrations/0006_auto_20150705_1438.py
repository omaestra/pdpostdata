# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0005_auto_20150705_1435'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='image_field',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='photo',
            old_name='thumbnail',
            new_name='image_cropped',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='thumbnail_height',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='thumbnail_width',
        ),
        migrations.AddField(
            model_name='photo',
            name='image_cropped_height',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='image_cropped_width',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_height',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_width',
            field=models.PositiveIntegerField(),
        ),
    ]
