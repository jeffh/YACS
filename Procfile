web: gunicorn yacs.wsgi -w 4
import_courses: python manage.py import_course_data && python manage.py create_section_cache
import_catalog: python manage.py import_catalog_data
clear_cache: python manage.py clear_cache
