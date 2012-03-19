# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Entry.selection_json'
        db.add_column('jslog_entry', 'selection_json', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Entry.selection_json'
        db.delete_column('jslog_entry', 'selection_json')


    models = {
        'jslog.cookie': {
            'Meta': {'object_name': 'Cookie'},
            'contents': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'jslog.entry': {
            'Meta': {'object_name': 'Entry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'log_history': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'raw': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'selection_json': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jslog.Cookie']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['jslog']
