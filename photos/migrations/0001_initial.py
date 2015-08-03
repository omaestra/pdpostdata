# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import photos.models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cropped',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_cropped', models.ImageField(verbose_name='Image', editable=False, upload_to=photos.models.get_image_path)),
                ('x', models.PositiveIntegerField(default=0, verbose_name='offset X')),
                ('y', models.PositiveIntegerField(default=0, verbose_name='offset Y')),
                ('w', models.PositiveIntegerField(null=True, verbose_name='cropped area width', blank=True)),
                ('h', models.PositiveIntegerField(null=True, verbose_name='cropped area height', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.CharField(default=photos.models.make_uuid, max_length=36, serialize=False, primary_key=True)),
                ('temp_hash', models.CharField(max_length=b'255')),
                ('message', models.TextField(max_length=b'120', blank=True)),
                ('image', models.ImageField(upload_to=photos.models.get_image_path)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cart_item', models.ForeignKey(blank=True, to='carts.CartItem', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='cropped',
            name='original',
            field=models.ForeignKey(related_name='cropped', verbose_name='Original image', to='photos.Photo'),
        ),
    ]
