web: gunicorn yacs.wsgi -w 4
beat: celery -A yacs beat -S djcelery.schedulers.DatabaseScheduler
worker: celery -A yacs worker -B
