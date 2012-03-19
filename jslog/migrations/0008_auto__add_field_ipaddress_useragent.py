# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'IPAddress.useragent'
        db.add_column('jslog_ipaddress', 'useragent', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'IPAddress.useragent'
        db.delete_column('jslog_ipaddress', 'useragent')


    models = {
        'jslog.entry': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Entry'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['jslog.IPAddress']", 'null': 'True', 'blank': 'True'}),
            'cookie': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localstorage_json': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'selection_json': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'jslog.ipaddress': {
            'Meta': {'object_name': 'IPAddress'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'useragent': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'})
        }
    }

    complete_apps = ['jslog']
