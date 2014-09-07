# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='is_comm_intense',
            field=models.BooleanField(default=False, verbose_name=b'Communication Intensive'),
        ),
    ]
