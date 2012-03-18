# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Entry.localstorage_json'
        db.add_column('jslog_entry', 'localstorage_json', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Entry.date_created'
        db.add_column('jslog_entry', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 3, 18, 2, 8, 7, 569959), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Entry.localstorage_json'
        db.delete_column('jslog_entry', 'localstorage_json')

        # Deleting field 'Entry.date_created'
        db.delete_column('jslog_entry', 'date_created')


    models = {
        'jslog.cookie': {
            'Meta': {'object_name': 'Cookie'},
            'contents': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'jslog.entry': {
            'Meta': {'object_name': 'Entry'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localstorage_json': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'selection_json': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jslog.Cookie']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['jslog']
