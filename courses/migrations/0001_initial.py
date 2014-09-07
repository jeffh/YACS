# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('number', models.IntegerField()),
                ('description', models.TextField(default=b'')),
                ('min_credits', models.IntegerField(verbose_name=b'Min Credits')),
                ('max_credits', models.IntegerField(verbose_name=b'Max Credits')),
                ('grade_type', models.CharField(default=b'', max_length=150, blank=True)),
                ('prereqs', models.TextField(default=b'')),
                ('is_comm_intense', models.BooleanField(verbose_name=b'Communication Intensive')),
            ],
            options={
                'ordering': ['department__code', 'number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=200, blank=True)),
                ('code', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'ordering': ['code'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OfferedFor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(help_text=b'Internal. Used by data source to identify unique offerings.', max_length=200, db_index=True, blank=True)),
                ('course', models.ForeignKey(related_name=b'offered_for', to='courses.Course')),
            ],
            options={
                'verbose_name': 'Offers',
                'verbose_name_plural': 'Offerings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.TimeField(default=None, null=True)),
                ('end', models.TimeField(default=None, null=True)),
                ('days_of_week_flag', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=5)),
                ('crn', models.IntegerField(unique=True)),
                ('seats_taken', models.IntegerField(verbose_name=b'Seats Taken')),
                ('seats_total', models.IntegerField(verbose_name=b'Seats Total')),
                ('notes', models.TextField(blank=True)),
                ('course', models.ForeignKey(related_name=b'sections', to='courses.Course')),
            ],
            options={
                'ordering': ['number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionCrosslisting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(help_text=b'Internal unique identification used by bridge module.', unique=True, max_length=200)),
            ],
            options={
                'verbose_name': 'Section Crosslisting',
                'verbose_name_plural': 'Section Crosslistings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instructor', models.CharField(max_length=150, blank=True)),
                ('location', models.CharField(max_length=150, blank=True)),
                ('kind', models.CharField(help_text=b'The kind of meeting time (eg - lab, recitation, lecture, etc.)', max_length=75)),
                ('period', models.ForeignKey(related_name=b'section_times', to='courses.Period')),
                ('section', models.ForeignKey(related_name=b'section_times', to='courses.Section')),
            ],
            options={
                'verbose_name': 'Section Period',
                'verbose_name_plural': 'Section Periods',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(help_text=b'The year the semester takes place')),
                ('month', models.IntegerField(help_text=b'The starting month of the semester')),
                ('name', models.CharField(help_text=b'An human-readable display of the semester', max_length=100)),
                ('ref', models.CharField(help_text=b'Internally used by bridge module to refer to a semester.', unique=True, max_length=150)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('visible', models.BooleanField(default=True, help_text=b'Should this semester be publicly visible?')),
            ],
            options={
                'ordering': ['-year', '-month'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SemesterDepartment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('department', models.ForeignKey(related_name=b'+', to='courses.Department')),
                ('semester', models.ForeignKey(related_name=b'+', to='courses.Semester')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='Slug')),
                ('color', colorful.fields.RGBColorField(blank=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tagged',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('content_type', models.ForeignKey(related_name='courses_tagged_tagged_items', verbose_name='Content type', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(related_name=b'courses_tagged_items', to='courses.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='semesterdepartment',
            unique_together=set([('department', 'semester')]),
        ),
        migrations.AlterUniqueTogether(
            name='semester',
            unique_together=set([('year', 'month')]),
        ),
        migrations.AddField(
            model_name='sectionperiod',
            name='semester',
            field=models.ForeignKey(related_name=b'section_times', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sectionperiod',
            unique_together=set([('period', 'section', 'semester')]),
        ),
        migrations.AddField(
            model_name='sectioncrosslisting',
            name='semester',
            field=models.ForeignKey(related_name=b'section_crosslistings', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='crosslisted',
            field=models.ForeignKey(related_name=b'sections', blank=True, to='courses.SectionCrosslisting', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='periods',
            field=models.ManyToManyField(related_name=b'sections', through='courses.SectionPeriod', to='courses.Period'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='semester',
            field=models.ForeignKey(related_name=b'sections', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('start', 'end', 'days_of_week_flag')]),
        ),
        migrations.AddField(
            model_name='offeredfor',
            name='semester',
            field=models.ForeignKey(related_name=b'offers', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='offeredfor',
            unique_together=set([('course', 'semester')]),
        ),
        migrations.AddField(
            model_name='department',
            name='semesters',
            field=models.ManyToManyField(related_name=b'departments', through='courses.SemesterDepartment', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(related_name=b'courses', to='courses.Department'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='semesters',
            field=models.ManyToManyField(related_name=b'courses', through='courses.OfferedFor', to='courses.Semester'),
            preserve_default=True,
        ),
    ]
