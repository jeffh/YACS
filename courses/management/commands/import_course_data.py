from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from courses.bridge import import_courses


class Command(BaseCommand):
    help = "Downloads the course data and imports it into the database."
    option_list = BaseCommand.option_list + (
        make_option('--force', '-f',
                    dest='force',
                    action='store_true',
                    default=False,
                    help='Force update of all semesters.'
                    ),
        make_option('--all', '-a',
                    dest='all',
                    action='store_true',
                    default=False,
                    help='Imports all semester course data that YACS can find.'
                    ),
        make_option('--no-catalog',
                    dest='no_catalog',
                    action='store_true',
                    default=False,
                    help='skips parsing the catalog'
                    ),
    )

    def handle(self, *args, **options):
        if options.get('force'):
            print "Forcing update..."
        import_courses(
            force=options.get('force'),
            all=options.get('all'),
            catalog=not options.get('no_catalog'),
        )
