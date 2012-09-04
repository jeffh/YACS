import os

from fabric.api import run, local, settings, cd, sudo
from fabric.contrib.project import upload_project
from fabric.contrib.files import append


APPS = 'api courses courses_viz scheduler'.split(' ')

DEPLOY_LOCATION = 'yacs'


def exists(name):
    with settings(warn_only=True):
        return not run('[ -e "%s" ]' % name).failed


def first_deploy():
    "Sets up the project for the initial deploy"
    run('virtualenv --distribute yacs_ve')


def deploy():
    "Deploys to the given system."
    clean()
    collectstatic()
    if not exists('yacs_ve'):
        run('virtualenv --distribute yacs_ve')
    PYTHON = '~/yacs_ve/bin/python'
    PIP = '~/yacs_ve/bin/pip'
    run('rm -rf yacs')
    upload_project()
    append('.bashrc', 'export YACS_ENV=production', use_sudo=True)
    with cd('yacs'):
        run(PIP + ' install --upgrade -r requirements/deployment.txt')
        # we're using postgres!
        # change to whatever you need to use
        run(PIP + ' install psycopg2')
        run(PYTHON + ' manage.py syncdb --noinput')
        run(PYTHON + ' manage.py migrate')
        run(PYTHON + ' manage.py collectstatic --noinput')


def collectstatic():
    local('python manage.py collectstatic --noinput')


def fetch():
    "Tells the deployment system to fetch course data."
    with cd('yacs'):
        run(PYTHON + ' manage.py import_course_data')
        run(PYTHON + ' manage.py create_section_cache')


def clean():
    "Removes local python cache files."
    local('find . -name "*.pyc" | xargs rm')
    local('find . -name "*.pyo" | xargs rm')
    local('find . -name "__pycache__" -type directory | xargs rm -r')
    with settings(warn_only=True):
        local('rm -r yacs/static/root')


def test():
    "Runs tests."
    clean()
    local('python manage.py test --failfast ' + ' '.join(APPS))
    local('pep8 . --exclude=migrations --statistics --count --ignore=E501')
