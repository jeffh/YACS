from django.core.management.base import BaseCommand
from yacs.courses.bridge import import_courses

class Command(BaseCommand):
	help = "Downloads the course data and imports it into the database."

	def handle(self, *args, **options):
		import_courses()