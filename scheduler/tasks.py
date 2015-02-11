from django.db import transaction
from django.conf import settings

from celery import shared_task

from yacs import celery_app
from courses.bridge import import_courses as bridge_import_courses
from courses.models import Semester
from scheduler import models


@shared_task
def compute_conflicts(all_semesters=False, sql=True):
    with transaction.atomic():
        semesters = Semester.objects.all()
        if not all_semesters:
            semesters = semesters[:1]
        for semester in semesters:
            print "Computing conflicts for %d-%d..." % (semester.year, semester.month)
            models.cache_conflicts(semester=semester, sql=sql)


@shared_task
def clear_selection_cache():
    with transaction.atomic():
        models.Selection.objects.all().update(api_cache='')
