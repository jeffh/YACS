# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from scheduler import models

def deserialize_numbers(numbers):
    return tuple(sorted(int(x) for x in numbers.split(',') if x))

def serialize_numbers(numbers):
    return ','.join(str(s) for s in numbers)

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for selection in orm.Selection.objects.all():
            # to counter a bug from old code... this string may show up.
            if selection.internal_crns == '[]':
                crns = []
            else:
                crns = deserialize_numbers(selection.internal_crns)
            sids = models.SectionProxy.objects.filter(crn__in=crns).values_list('id', flat=True)
            selection.internal_section_ids = serialize_numbers(sids)
            selection.save()


    def backwards(self, orm):
        "Write your backwards methods here."
        for selection in orm.Selection.objects.all():
            sids = deserialize_numbers(selection.internal_section_ids)
            crns = models.SectionProxy.objects.filter(id__in=sids).values_list('crn', flat=True)
            selection.internal_crns = serialize_numbers(crns)
            selection.save()


    models = {
        'courses.course': {
            'Meta': {'ordering': "['department__code', 'number']", 'unique_together': "(('name', 'department', 'number'),)", 'object_name': 'Course'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'courses'", 'to': "orm['courses.Department']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
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
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sections'", 'symmetrical': 'False', 'through': "orm['courses.SectionPeriod']", 'to': "orm['courses.Period']"}),
            'seats_taken': ('django.db.models.fields.IntegerField', [], {}),
            'seats_total': ('django.db.models.fields.IntegerField', [], {}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['courses.Semester']"})
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
            'Meta': {'ordering': "['-year', '-month']", 'unique_together': "(('year', 'month'),)", 'object_name': 'Semester'},
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
        'scheduler.sectionconflict': {
            'Meta': {'unique_together': "(('section1', 'section2', 'semester'),)", 'object_name': 'SectionConflict'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Section']"}),
            'section2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['courses.Section']"}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_conflicts'", 'to': "orm['courses.Semester']"})
        },
        'scheduler.selection': {
            'Meta': {'object_name': 'Selection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_crns': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'internal_section_ids': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'internal_slug': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['scheduler']
