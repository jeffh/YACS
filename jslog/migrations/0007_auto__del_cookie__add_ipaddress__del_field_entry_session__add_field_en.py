# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Cookie'
        db.delete_table('jslog_cookie')

        # Adding model 'IPAddress'
        db.create_table('jslog_ipaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('jslog', ['IPAddress'])

        # Deleting field 'Entry.session'
        db.delete_column('jslog_entry', 'session_id')

        # Adding field 'Entry.address'
        db.add_column('jslog_entry', 'address', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['jslog.IPAddress'], null=True, blank=True), keep_default=False)

        # Adding field 'Entry.cookie'
        db.add_column('jslog_entry', 'cookie', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'Cookie'
        db.create_table('jslog_cookie', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contents', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('jslog', ['Cookie'])

        # Deleting model 'IPAddress'
        db.delete_table('jslog_ipaddress')

        # User chose to not deal with backwards NULL issues for 'Entry.session'
        raise RuntimeError("Cannot reverse this migration. 'Entry.session' and its values cannot be restored.")

        # Deleting field 'Entry.address'
        db.delete_column('jslog_entry', 'address_id')

        # Deleting field 'Entry.cookie'
        db.delete_column('jslog_entry', 'cookie')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['jslog']
