from django.core.management.base import BaseCommand, CommandError
from courses.bridge.rpi import import_catalog

class Command(BaseCommand):
	help = 'Imports the course information from the RPI Catalog'
	
	def handle(self, *args, **options):
		import_catalog()
