
from django.utils.importlib import import_module

def import_courses(force=False):
    "Runs the course importer specified in settings.py"
    from django.db import transaction

    with transaction.commit_on_success():
        from django.conf import settings

        module, funcname = settings.COURSES_COLLEGE_PARSER.rsplit('.', 1)
        mod = import_module(module)
        getattr(mod, funcname)(force=force)
