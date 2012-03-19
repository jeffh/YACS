from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.bridge import import_courses


class Command(BaseCommand):
    help = "Downloads the course data and imports it into the database."
    option_list = BaseCommand.option_list + (
        make_option('--force', '-f', dest='force', action='store_true',
            default=False,
            help='Force update of all semesters.'),
        make_option('--all', '-a', dest='all', action='store_true',
            default=False,
            help='Imports all semester course data that YACS can find.'),
    )

    def handle(self, *args, **options):
        if options.get('force'):
            print "Forcing update..."
        #with transaction.commit_on_success():
        #    import_courses(force=options.get('force', False))
        import_courses(
            force=options.get('force'),
            all=options.get('all')
        )
