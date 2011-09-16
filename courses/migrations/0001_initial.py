# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Department'
        db.create_table('courses_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('courses', ['Department'])

        # Adding model 'Semester'
        db.create_table('courses_semester', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('month', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('ref', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('courses', ['Semester'])

        # Adding unique constraint on 'Semester', fields ['year', 'month']
        db.create_unique('courses_semester', ['year', 'month'])

        # Adding model 'Period'
        db.create_table('courses_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('end_time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True)),
            ('days_of_week_raw', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('courses', ['Period'])

        # Adding unique constraint on 'Period', fields ['start_time', 'end_time', 'days_of_week_raw']
        db.create_unique('courses_period', ['start_time', 'end_time', 'days_of_week_raw'])

        # Adding model 'SectionCrosslisting'
        db.create_table('courses_sectioncrosslisting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='section_crosslistings', to=orm['courses.Semester'])),
            ('ref', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('courses', ['SectionCrosslisting'])

        # Adding model 'Section'
        db.create_table('courses_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('crn', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sections', to=orm['courses.Course'])),
            ('crosslisted', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sections', null=True, to=orm['courses.SectionCrosslisting'])),
            ('seats_taken', self.gf('django.db.models.fields.IntegerField')()),
            ('seats_total', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('courses', ['Section'])

        # Adding model 'Course'
        db.create_table('courses_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='courses', to=orm['courses.Department'])),
            ('min_credits', self.gf('django.db.models.fields.IntegerField')()),
            ('max_credits', self.gf('django.db.models.fields.IntegerField')()),
            ('grade_type', self.gf('django.db.models.fields.CharField')(default='', max_length=150, blank=True)),
        ))
        db.send_create_signal('courses', ['Course'])

        # Adding unique constraint on 'Course', fields ['department', 'number']
        db.create_unique('courses_course', ['department_id', 'number'])

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

        # Removing unique constraint on 'Course', fields ['department', 'number']
        db.delete_unique('courses_course', ['department_id', 'number'])

        # Removing unique constraint on 'Period', fields ['start_time', 'end_time', 'days_of_week_raw']
        db.delete_unique('courses_period', ['start_time', 'end_time', 'days_of_week_raw'])

        # Removing unique constraint on 'Semester', fields ['year', 'month']
        db.delete_unique('courses_semester', ['year', 'month'])

        # Deleting model 'Department'
        db.delete_table('courses_department')

        # Deleting model 'Semester'
        db.delete_table('courses_semester')

        # Deleting model 'Period'
        db.delete_table('courses_period')

        # Deleting model 'SectionCrosslisting'
        db.delete_table('courses_sectioncrosslisting')

        # Deleting model 'Section'
        db.delete_table('courses_section')

        # Deleting model 'Course'
        db.delete_table('courses_course')

        # Deleting model 'OfferedFor'
        db.delete_table('courses_offeredfor')

        # Deleting model 'SectionPeriod'
        db.delete_table('courses_sectionperiod')


    models = {
        'courses.course': {
            'Meta': {'unique_together': "(('department', 'number'),)", 'object_name': 'Course'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': "orm['courses.Department']"}),
            'grade_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_credits': ('django.db.models.fields.IntegerField', [], {}),
            'min_credits': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'semester': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': "orm['courses.OfferedFor']", 'to': "orm['courses.Semester']"})
        },
        'courses.department': {
            'Meta': {'object_name': 'Department'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
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
            'end_time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'})
        },
        'courses.section': {
            'Meta': {'object_name': 'Section'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['courses.Course']"}),
            'crn': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'crosslisted': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sections'", 'null': 'True', 'to': "orm['courses.SectionCrosslisting']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': "orm['courses.SectionPeriod']", 'to': "orm['courses.Period']"}),
            'seats_taken': ('django.db.models.fields.IntegerField', [], {}),
            'seats_total': ('django.db.models.fields.IntegerField', [], {})
        },
        'courses.sectioncrosslisting': {
            'Meta': {'object_name': 'SectionCrosslisting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_crosslistings'", 'to': "orm['courses.Semester']"})
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
            'Meta': {'unique_together': "(('year', 'month'),)", 'object_name': 'Semester'},
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['courses']
