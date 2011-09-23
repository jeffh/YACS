# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Schedule', fields ['semester', 'crns_used', 'course_ids_used']
        db.delete_unique('scheduler_schedule', ['semester_id', 'crns_used', 'course_ids_used'])

        # Adding unique constraint on 'Schedule', fields ['semester', 'crns_used']
        db.create_unique('scheduler_schedule', ['semester_id', 'crns_used'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Schedule', fields ['semester', 'crns_used']
        db.delete_unique('scheduler_schedule', ['semester_id', 'crns_used'])

        # Adding unique constraint on 'Schedule', fields ['semester', 'crns_used', 'course_ids_used']
        db.create_unique('scheduler_schedule', ['semester_id', 'crns_used', 'course_ids_used'])


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
            'semesters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': "orm['courses.OfferedFor']", 'to': "orm['courses.Semester']"})
        },
        'courses.department': {
            'Meta': {'ordering': "['code']", 'object_name': 'Department'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'semesters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'departments'", 'symmetrical': 'False', 'through': "orm['courses.SemesterDepartment']", 'to': "orm['courses.Semester']"})
        },
        'courses.offeredfor': {
            'Meta': {'unique_together': "(('course', 'semester'),)", 'object_name': 'OfferedFor'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offered_for'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': "orm['courses.Semester']"})
        },
        'courses.period': {
            'Meta': {'unique_together': "(('start', 'end', 'days_of_week_flag'),)", 'object_name': 'Period'},
            'days_of_week_flag': ('django.db.models.fields.IntegerField', [], {}),
            'end': ('django.db.models.fields.TimeField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'default': 'None', 'null': 'True'})
        },
        'courses.section': {
            'Meta': {'ordering': "['number']", 'object_name': 'Section'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['courses.Course']"}),
            'crn': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'crosslisted': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sections'", 'null': 'True', 'to': "orm['courses.SectionCrosslisting']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': "orm['courses.SectionPeriod']", 'to': "orm['courses.Period']"}),
            'seats_taken': ('django.db.models.fields.IntegerField', [], {}),
            'seats_total': ('django.db.models.fields.IntegerField', [], {}),
            'semesters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sections'", 'symmetrical': 'False', 'through': "orm['courses.SemesterSection']", 'to': "orm['courses.Semester']"})
        },
        'courses.sectioncrosslisting': {
            'Meta': {'object_name': 'SectionCrosslisting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_crosslistings'", 'to': "orm['courses.Semester']"})
        },
        'courses.sectionperiod': {
            'Meta': {'unique_together': "(('period', 'section', 'semester'),)", 'object_name': 'SectionPeriod'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_times'", 'to': "orm['courses.Period']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_times'", 'to': "orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_times'", 'to': "orm['courses.Semester']"})
        },
        'courses.semester': {
            'Meta': {'unique_together': "(('year', 'month'),)", 'object_name': 'Semester'},
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'courses.semesterdepartment': {
            'Meta': {'unique_together': "(('department', 'semester'),)", 'object_name': 'SemesterDepartment'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Semester']"})
        },
        'courses.semestersection': {
            'Meta': {'object_name': 'SemesterSection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Semester']"})
        },
        'scheduler.courseinschedule': {
            'Meta': {'unique_together': "(('schedule', 'course'),)", 'object_name': 'CourseInSchedule'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'course_in_schedules'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses_in_schedule'", 'to': "orm['scheduler.Schedule']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Semester']"})
        },
        'scheduler.schedule': {
            'Meta': {'unique_together': "(('crns_used', 'semester'),)", 'object_name': 'Schedule'},
            'course_ids_used': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'schedules'", 'symmetrical': 'False', 'through': "orm['scheduler.CourseInSchedule']", 'to': "orm['courses.Course']"}),
            'crns_used': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'schedules'", 'symmetrical': 'False', 'through': "orm['scheduler.SectionInSchedule']", 'to': "orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schedules'", 'to': "orm['courses.Semester']"})
        },
        'scheduler.sectioninschedule': {
            'Meta': {'unique_together': "(('schedule', 'section'),)", 'object_name': 'SectionInSchedule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections_in_schedule'", 'to': "orm['scheduler.Schedule']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_in_schedules'", 'to': "orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Semester']"})
        }
    }

    complete_apps = ['scheduler']
