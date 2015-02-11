from celery import shared_task

from django.conf import settings

from courses.bridge import import_courses as bridge_import_courses

@shared_task
def import_courses(force=False, all=False, catalog=True):
    bridge_import_courses(force=force, all=all, catalog=catalog)

