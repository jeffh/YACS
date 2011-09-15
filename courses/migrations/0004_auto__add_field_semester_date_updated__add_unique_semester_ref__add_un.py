# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Semester.date_updated'
        db.add_column('courses_semester', 'date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2011, 9, 15, 11, 2, 55, 143681), blank=True), keep_default=False)

        # Adding unique constraint on 'Semester', fields ['ref']
        db.create_unique('courses_semester', ['ref'])

        # Adding unique constraint on 'Semester', fields ['school', 'ref']
        db.create_unique('courses_semester', ['school_id', 'ref'])

        # Adding unique constraint on 'Semester', fields ['school', 'month', 'year']
        db.create_unique('courses_semester', ['school_id', 'month', 'year'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Semester', fields ['school', 'month', 'year']
        db.delete_unique('courses_semester', ['school_id', 'month', 'year'])

        # Removing unique constraint on 'Semester', fields ['school', 'ref']
        db.delete_unique('courses_semester', ['school_id', 'ref'])

        # Removing unique constraint on 'Semester', fields ['ref']
        db.delete_unique('courses_semester', ['ref'])

        # Deleting field 'Semester.date_updated'
        db.delete_column('courses_semester', 'date_updated')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'crosslistings'", 'unique': 'True', 'to': "orm['courses.Semester']"})
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
            'Meta': {'unique_together': "(('school', 'ref'), ('school', 'year', 'month'))", 'object_name': 'Semester'},
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.School']"}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['courses']
