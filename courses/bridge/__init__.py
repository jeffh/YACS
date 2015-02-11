from django.utils.importlib import import_module


def import_courses(*args, **kwargs):
    "Runs the course importer specified in settings.py"
    from django.db import transaction

    with transaction.atomic():
        from django.conf import settings

        module, funcname = settings.COURSES_COLLEGE_PARSER.rsplit('.', 1)
        mod = import_module(module)
        getattr(mod, funcname)(*args, **kwargs)

