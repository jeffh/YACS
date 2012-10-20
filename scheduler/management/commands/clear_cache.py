from optparse import make_option

from django.core.management.base import BaseCommand

from shortcuts import commit_all_or_rollback

from scheduler import models


class Command(BaseCommand):
    help = "Removes all caches on Selection model"
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        with commit_all_or_rollback():
            models.Selection.objects.all().update(api_cache='')
