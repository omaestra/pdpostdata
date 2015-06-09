# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(max_length=120)),
                ('rate', models.DecimalField(max_digits=1, decimal_places=0, choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default=b'Pendiente', max_length=120, choices=[(b'Pendiente', b'Pendiente'), (b'Iniciado', b'Iniciado'), (b'Rechazado', b'Rechazado'), (b'Imprimiendo', b'Imprimiendo'), (b'Enviado', b'Enviado')]),
        ),
        migrations.AddField(
            model_name='orderrating',
            name='order',
            field=models.ForeignKey(to='orders.Order'),
        ),
    ]
