FROM tutum/buildstep
EXPOSE 8000

# production: 'production'
ENV YACS_ENV development

# secret seed for django
ENV YACS_SECRET 'secret'

# database url for YACS to use
# production: 'postgres://user:pass@host:port/db'
ENV YACS_DATABASE_URL 'postgres://user:pass@host:port/db'

# comma-separated list of memcache servers (IP:PORT,IP:PORT)
ENV MEMCACHE_SERVERS '127.0.0.1:11211'
#ENV MEMCACHE_USERNAME ''
#ENV MEMCACHE_PASSWORD ''

# if you don't want YACS to log to the file system
#ENV YACS_DISABLE_FILE_SYSTEM_LOGGING 'YES'

CMD ["django_gunicorn yacs.settings"]