# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_auto_20141020_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='number',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='code',
            field=models.CharField(unique=True, max_length=50, db_index=True),
        ),
    ]
