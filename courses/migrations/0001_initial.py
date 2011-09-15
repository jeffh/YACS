# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'School'
        db.create_table('courses_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('parser_function', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('courses', ['School'])

        # Adding model 'Department'
        db.create_table('courses_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(related_name='departments', to=orm['courses.School'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('courses', ['Department'])

        # Adding model 'Semester'
        db.create_table('courses_semester', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courses.School'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('month', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('courses', ['Semester'])

        # Adding model 'Period'
        db.create_table('courses_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.IntegerField')()),
            ('end_time', self.gf('django.db.models.fields.IntegerField')()),
            ('days_of_week_raw', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('courses', ['Period'])

        # Adding unique constraint on 'Period', fields ['start_time', 'end_time', 'days_of_week_raw']
        db.create_unique('courses_period', ['start_time', 'end_time', 'days_of_week_raw'])

        # Adding model 'Section'
        db.create_table('courses_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('crn', self.gf('django.db.models.fields.IntegerField')()),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sections', to=orm['courses.Course'])),
            ('seats_taken', self.gf('django.db.models.fields.IntegerField')()),
            ('seats_total', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('courses', ['Section'])

        # Adding unique constraint on 'Section', fields ['number', 'course']
        db.create_unique('courses_section', ['number', 'course_id'])

        # Adding model 'Crosslisting'
        db.create_table('courses_crosslisting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('courses', ['Crosslisting'])

        # Adding model 'Course'
        db.create_table('courses_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['courses.School'])),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['courses.Department'])),
            ('crosslisted', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['courses.Crosslisting'])),
            ('min_credits', self.gf('django.db.models.fields.IntegerField')()),
            ('max_credits', self.gf('django.db.models.fields.IntegerField')()),
            ('grade_type', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('courses', ['Course'])

        # Adding unique constraint on 'Course', fields ['name', 'number', 'school']
        db.create_unique('courses_course', ['name', 'number', 'school_id'])

        # Adding model 'OfferedFor'
        db.create_table('courses_offeredfor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offered_for', to=orm['courses.Course'])),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offers', to=orm['courses.Semester'])),
        ))
        db.send_create_signal('courses', ['OfferedFor'])

        # Adding unique constraint on 'OfferedFor', fields ['course', 'semester']
        db.create_unique('courses_offeredfor', ['course_id', 'semester_id'])

        # Adding model 'SectionPeriod'
        db.create_table('courses_sectionperiod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(related_name='course_times', to=orm['courses.Period'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(related_name='course_times', to=orm['courses.Section'])),
            ('instructor', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=75)),
        ))
        db.send_create_signal('courses', ['SectionPeriod'])

        # Adding unique constraint on 'SectionPeriod', fields ['period', 'section']
        db.create_unique('courses_sectionperiod', ['period_id', 'section_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'SectionPeriod', fields ['period', 'section']
        db.delete_unique('courses_sectionperiod', ['period_id', 'section_id'])

        # Removing unique constraint on 'OfferedFor', fields ['course', 'semester']
        db.delete_unique('courses_offeredfor', ['course_id', 'semester_id'])

        # Removing unique constraint on 'Course', fields ['name', 'number', 'school']
        db.delete_unique('courses_course', ['name', 'number', 'school_id'])

        # Removing unique constraint on 'Section', fields ['number', 'course']
        db.delete_unique('courses_section', ['number', 'course_id'])

        # Removing unique constraint on 'Period', fields ['start_time', 'end_time', 'days_of_week_raw']
        db.delete_unique('courses_period', ['start_time', 'end_time', 'days_of_week_raw'])

        # Deleting model 'School'
        db.delete_table('courses_school')

        # Deleting model 'Department'
        db.delete_table('courses_department')

        # Deleting model 'Semester'
        db.delete_table('courses_semester')

        # Deleting model 'Period'
        db.delete_table('courses_period')

        # Deleting model 'Section'
        db.delete_table('courses_section')

        # Deleting model 'Crosslisting'
        db.delete_table('courses_crosslisting')

        # Deleting model 'Course'
        db.delete_table('courses_course')

        # Deleting model 'OfferedFor'
        db.delete_table('courses_offeredfor')

        # Deleting model 'SectionPeriod'
        db.delete_table('courses_sectionperiod')


    models = {
        'courses.course': {
            'Meta': {'unique_together': "(('name', 'number', 'school'),)", 'object_name': 'Course'},
            'crosslisted': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': "orm['courses.Crosslisting']"}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': "orm['courses.Department']"}),
            'grade_type': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_credits': ('django.db.models.fields.IntegerField', [], {}),
            'min_credits': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': "orm['courses.School']"}),
            'semester': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': "orm['courses.OfferedFor']", 'to': "orm['courses.Semester']"})
        },
        'courses.crosslisting': {
            'Meta': {'object_name': 'Crosslisting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'courses.department': {
            'Meta': {'object_name': 'Department'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'departments'", 'to': "orm['courses.School']"})
        },
        'courses.offeredfor': {
            'Meta': {'unique_together': "(('course', 'semester'),)", 'object_name': 'OfferedFor'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offered_for'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': "orm['courses.Semester']"})
        },
        'courses.period': {
            'Meta': {'unique_together': "(('start_time', 'end_time', 'days_of_week_raw'),)", 'object_name': 'Period'},
            'days_of_week_raw': ('django.db.models.fields.IntegerField', [], {}),
            'end_time': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.IntegerField', [], {})
        },
        'courses.school': {
            'Meta': {'object_name': 'School'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parser_function': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'courses.section': {
            'Meta': {'unique_together': "(('number', 'course'),)", 'object_name': 'Section'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['courses.Course']"}),
            'crn': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': "orm['courses.SectionPeriod']", 'to': "orm['courses.Period']"}),
            'seats_taken': ('django.db.models.fields.IntegerField', [], {}),
            'seats_total': ('django.db.models.fields.IntegerField', [], {})
        },
        'courses.sectionperiod': {
            'Meta': {'unique_together': "(('period', 'section'),)", 'object_name': 'SectionPeriod'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'course_times'", 'to': "orm['courses.Period']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'course_times'", 'to': "orm['courses.Section']"})
        },
        'courses.semester': {
            'Meta': {'object_name': 'Semester'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.School']"}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['courses']
