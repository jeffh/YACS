from django.db import models


class IPAddress(models.Model):
    address = models.IPAddressField()
    useragent = models.CharField(max_length=255, default='')

    class Meta:
        unique_together = ('address', 'useragent')
        verbose_name = 'IP Address'
        verbose_name_plural = 'IP Addresses'

    def __unicode__(self):
        return "<IPAddress: %s - %s>" % (self.address, self.useragent)


class Entry(models.Model):
    address = models.ForeignKey(IPAddress, default=None, null=True, blank=True)
    cookie = models.CharField(max_length=255, default='')
    url = models.CharField(max_length=255)
    message = models.TextField(blank=True, default='')
    meta = models.TextField(default='', blank=True)
    selection_json = models.TextField(blank=True, default='')
    localstorage_json = models.TextField(blank=True, default='')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Entries'
        ordering = ['-date_created']

    def __unicode__(self):
        return u"<Entry: %r: %r>" % (self.address, self.message or '')
