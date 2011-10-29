from django.core.management.base import BaseCommand
from django.db import transaction
from yacs.courses.models import Semester
from yacs.scheduler import models
from optparse import make_option

class Command(BaseCommand):
    help = "Caches all the section conflicts into the database."
    option_list = BaseCommand.option_list + (
        make_option('--all', '-a', dest='all', action='store_true',
            help='Force update of all semesters instead of just the latest one.'),
    )

    def handle(self, *args, **options):
        with transaction.commit_on_success():
            semesters = Semester.objects.all()
            if not options.get('all'):
                semesters = semesters[:1]

            for semester in semesters:
                print "Computing conflicts for %d-%d..." % (semester.year, semester.month)
                models.cache_conflicts(semester=semester)


