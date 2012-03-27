from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from courses.bridge.rpi import import_catalog


class Command(BaseCommand):
    help = 'Imports the course information from the RPI Catalog'
    option_list = BaseCommand.option_list + (
        make_option('--all', '-a', dest='all', action='store_true', help="parse ALL the catalog data from all the available catalogs"),
    )

    def handle(self, *args, **options):
        import_catalog(a=options.get('all', False))
