# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Cookie'
        db.create_table('jslog_cookie', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contents', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('jslog', ['Cookie'])

        # Adding model 'Entry'
        db.create_table('jslog_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jslog.Cookie'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('line_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('log_history', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('raw', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('jslog', ['Entry'])


    def backwards(self, orm):
        
        # Deleting model 'Cookie'
        db.delete_table('jslog_cookie')

        # Deleting model 'Entry'
        db.delete_table('jslog_entry')


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
            'message': ('django.db.models.fields.TextField', [], {}),
            'raw': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jslog.Cookie']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['jslog']
