# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20140907_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='crn',
            field=models.IntegerField(db_index=True),
        ),
    ]
