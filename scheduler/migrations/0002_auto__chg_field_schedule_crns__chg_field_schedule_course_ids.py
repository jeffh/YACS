# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Schedule.crns'
        db.alter_column('scheduler_schedule', 'crns', self.gf('timetable.scheduler.fields.SetOfIntegersField')(unique=True))

        # Changing field 'Schedule.course_ids'
        db.alter_column('scheduler_schedule', 'course_ids', self.gf('timetable.scheduler.fields.SetOfIntegersField')())


    def backwards(self, orm):
        
        # Changing field 'Schedule.crns'
        db.alter_column('scheduler_schedule', 'crns', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=200, unique=True))

        # Changing field 'Schedule.course_ids'
        db.alter_column('scheduler_schedule', 'course_ids', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=200))


    models = {
        'courses.semester': {
            'Meta': {'unique_together': "(('year', 'month'),)", 'object_name': 'Semester'},
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'scheduler.schedule': {
            'Meta': {'unique_together': "(('crns', 'semester'),)", 'object_name': 'Schedule'},
            'course_ids': ('timetable.scheduler.fields.SetOfIntegersField', [], {'db_index': 'True'}),
            'crns': ('timetable.scheduler.fields.SetOfIntegersField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schedules'", 'to': "orm['courses.Semester']"})
        }
    }

    complete_apps = ['scheduler']
