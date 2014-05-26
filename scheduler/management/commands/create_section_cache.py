from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Semester
from scheduler import models


class Command(BaseCommand):
    help = "Caches all the section conflicts into the database."
    option_list = BaseCommand.option_list + (
        make_option('--all', '-a', dest='all', action='store_true',
            help='Force update of all semesters instead of just the latest one.'),
        make_option('--sql', '-s', dest='sql', action='store_false', default=True,
            help='Use manual SQL Insertion instead of Django objects to insert conflicts.'),
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            semesters = Semester.objects.all()
            if not options.get('all', False):
                semesters = semesters[:1]
            for semester in semesters:
                print "Computing conflicts for %d-%d..." % (semester.year, semester.month)
                models.cache_conflicts(semester=semester, sql=options.get('sql'))
