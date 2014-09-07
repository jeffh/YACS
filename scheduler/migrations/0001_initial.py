# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedSelection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_section_ids', models.CommaSeparatedIntegerField(max_length=1024, db_index=True)),
                ('internal_blocked_times', models.TextField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionConflict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section1', models.ForeignKey(related_name=b'+', to='courses.Section')),
                ('section2', models.ForeignKey(related_name=b'+', to='courses.Section')),
                ('semester', models.ForeignKey(related_name=b'section_conflicts', to='courses.Semester')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_section_ids', models.CommaSeparatedIntegerField(max_length=255)),
                ('api_cache', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sectionconflict',
            unique_together=set([('section1', 'section2', 'semester')]),
        ),
    ]
