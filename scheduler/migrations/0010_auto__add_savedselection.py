# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SavedSelection'
        db.create_table(u'scheduler_savedselection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('internal_section_ids', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=1024)),
            ('internal_blocked_times', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal(u'scheduler', ['SavedSelection'])


    def backwards(self, orm):
        # Deleting model 'SavedSelection'
        db.delete_table(u'scheduler_savedselection')


    models = {
        u'courses.course': {
            'Meta': {'ordering': "['department__code', 'number']", 'object_name': 'Course'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': u"orm['courses.Department']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'grade_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_comm_intense': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_credits': ('django.db.models.fields.IntegerField', [], {}),
            'min_credits': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'prereqs': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'semesters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'courses'", 'symmetrical': 'False', 'through': u"orm['courses.OfferedFor']", 'to': u"orm['courses.Semester']"})
        },
        u'courses.department': {
            'Meta': {'ordering': "['code']", 'object_name': 'Department'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'semesters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'departments'", 'symmetrical': 'False', 'through': u"orm['courses.SemesterDepartment']", 'to': u"orm['courses.Semester']"})
        },
        u'courses.offeredfor': {
            'Meta': {'unique_together': "(('course', 'semester'),)", 'object_name': 'OfferedFor'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offered_for'", 'to': u"orm['courses.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ref': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': u"orm['courses.Semester']"})
        },
        u'courses.period': {
            'Meta': {'unique_together': "(('start', 'end', 'days_of_week_flag'),)", 'object_name': 'Period'},
            'days_of_week_flag': ('django.db.models.fields.IntegerField', [], {}),
            'end': ('django.db.models.fields.TimeField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.TimeField', [], {'default': 'None', 'null': 'True'})
        },
        u'courses.section': {
            'Meta': {'ordering': "['number']", 'object_name': 'Section'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': u"orm['courses.Course']"}),
            'crn': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'crosslisted': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sections'", 'null': 'True', 'to': u"orm['courses.SectionCrosslisting']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sections'", 'symmetrical': 'False', 'through': u"orm['courses.SectionPeriod']", 'to': u"orm['courses.Period']"}),
            'seats_taken': ('django.db.models.fields.IntegerField', [], {}),
            'seats_total': ('django.db.models.fields.IntegerField', [], {}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': u"orm['courses.Semester']"})
        },
        u'courses.sectioncrosslisting': {
            'Meta': {'object_name': 'SectionCrosslisting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_crosslistings'", 'to': u"orm['courses.Semester']"})
        },
        u'courses.sectionperiod': {
            'Meta': {'unique_together': "(('period', 'section', 'semester'),)", 'object_name': 'SectionPeriod'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_times'", 'to': u"orm['courses.Period']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_times'", 'to': u"orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_times'", 'to': u"orm['courses.Semester']"})
        },
        u'courses.semester': {
            'Meta': {'ordering': "['-year', '-month']", 'unique_together': "(('year', 'month'),)", 'object_name': 'Semester'},
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'courses.semesterdepartment': {
            'Meta': {'unique_together': "(('department', 'semester'),)", 'object_name': 'SemesterDepartment'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['courses.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['courses.Semester']"})
        },
        u'scheduler.savedselection': {
            'Meta': {'object_name': 'SavedSelection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_blocked_times': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '1024', 'blank': 'True'}),
            'internal_section_ids': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '1024'})
        },
        u'scheduler.sectionconflict': {
            'Meta': {'unique_together': "(('section1', 'section2', 'semester'),)", 'object_name': 'SectionConflict'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['courses.Section']"}),
            'section2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_conflicts'", 'to': u"orm['courses.Semester']"})
        },
        u'scheduler.selection': {
            'Meta': {'object_name': 'Selection'},
            'api_cache': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_section_ids': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['scheduler']