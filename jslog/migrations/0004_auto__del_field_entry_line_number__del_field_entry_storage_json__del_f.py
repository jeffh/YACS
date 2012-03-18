# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Entry.line_number'
        db.delete_column('jslog_entry', 'line_number')

        # Deleting field 'Entry.storage_json'
        db.delete_column('jslog_entry', 'storage_json')

        # Deleting field 'Entry.selection_json'
        db.delete_column('jslog_entry', 'selection_json')

        # Deleting field 'Entry.raw'
        db.delete_column('jslog_entry', 'raw')

        # Deleting field 'Entry.log_history'
        db.delete_column('jslog_entry', 'log_history')

        # Adding field 'Entry.meta'
        db.add_column('jslog_entry', 'meta', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Entry.line_number'
        db.add_column('jslog_entry', 'line_number', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Entry.storage_json'
        db.add_column('jslog_entry', 'storage_json', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Entry.selection_json'
        db.add_column('jslog_entry', 'selection_json', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Entry.raw'
        db.add_column('jslog_entry', 'raw', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Entry.log_history'
        db.add_column('jslog_entry', 'log_history', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Deleting field 'Entry.meta'
        db.delete_column('jslog_entry', 'meta')


    models = {
        'jslog.cookie': {
            'Meta': {'object_name': 'Cookie'},
            'contents': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'jslog.entry': {
            'Meta': {'object_name': 'Entry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jslog.Cookie']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['jslog']
