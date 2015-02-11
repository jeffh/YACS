from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Semester
from scheduler import models
from scheduler.tasks import compute_conflicts


class Command(BaseCommand):
    help = "Caches all the section conflicts into the database."
    option_list = BaseCommand.option_list + (
        make_option('--all', '-a',
                    dest='all',
                    action='store_true',
                    help='Force update of all semesters instead of just the latest one.'),
        make_option('--sql', '-s',
                    dest='sql',
                    action='store_false',
                    default=True,
                    help='Use manual SQL Insertion instead of Django objects to insert conflicts.'),
    )

    def handle(self, *args, **options):
        compute_conflicts(all_semester=options.get('all', False),
                          sql=options.get('sql'))

