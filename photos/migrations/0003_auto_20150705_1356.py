# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_photo_cart_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('crop_x', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('crop_y', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('crop_w', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('crop_h', models.PositiveIntegerField(default=0, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('slug', models.SlugField()),
                ('height', models.PositiveIntegerField(null=True, blank=True)),
                ('width', models.PositiveIntegerField(null=True, blank=True)),
                ('aspect_ratio', models.FloatField(null=True, blank=True)),
                ('auto_crop', models.BooleanField(default=False)),
                ('retina', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SizeSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='photo',
            name='image_field',
        ),
        migrations.AddField(
            model_name='photo',
            name='temp_hash',
            field=models.CharField(default=3432532, max_length=b'255'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photo',
            name='cart_item',
            field=models.ForeignKey(blank=True, to='carts.CartItem', null=True),
        ),
        migrations.AddField(
            model_name='size',
            name='size_set',
            field=models.ForeignKey(to='photos.SizeSet', null=True),
        ),
    ]
