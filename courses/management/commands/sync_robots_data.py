from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib.sites.models import Site
from optparse import make_option
import sys

from yacs.courses import models
from yacs.courses.signals import robots_signal

class Command(BaseCommand):
    help = "Creates and updates data for robots.txt (requires django-robots to be installed)."

    def get_or_create_url(self, name, **kwargs):
        from robots.models import Url
        url, _ = Url.objects.get_or_create(pattern=reverse(name, kwargs=kwargs))
        return url

    def handle(self, *args, **options):
        from robots.models import Url
        try:
            from robots.models import Rule
        except ImportError:
            print >>sys.stderr, "ImportError: Could not find django-robots."
            sys.exit(1)

        with transaction.commit_on_success():
            site = Site.objects.get_current()
            rule, _ = Rule.objects.get_or_create(
                robot='*',
            )
            rule.sites.add(site)
            root_url, _ = Url.objects.get_or_create(pattern='/')
            rule.allowed.add(root_url)
            for semester in models.Semester.objects.all():
                url = self.get_or_create_url('departments', year=semester.year, month=semester.month)
                rule.allowed.add(url)

                for department in semester.departments.all():
                    url = self.get_or_create_url('courses-by-dept', year=semester.year, month=semester.month, code=department.code)
                    rule.allowed.add(url)

                url = self.get_or_create_url('selected-courses', year=semester.year, month=semester.month)
                rule.disallowed.add(url)

                robots_signal.send(sender=self, semester=semester, rule=rule)

