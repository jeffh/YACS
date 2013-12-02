import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from courses import models


class SemesterSitemap(Sitemap):
    def items(self):
        return models.Semester.objects.all().order_by('-year', '-month')

    def lastmod(self, obj):
        return obj.date_updated

    def location(self, obj):
        r = reverse('departments', kwargs=dict(year=obj.year, month=obj.month))
        print r
        return r

    def changefreq(self, item):
        latest = models.Semester.objects.all().order_by('-year', '-month')[0]
        if latest == item:
            return 'hourly'
        return 'monthly'


sitemaps = {
    'semesters': SemesterSitemap,
}
