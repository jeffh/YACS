from fabric.api import roles, env
from fabric.context_managers import cd, prefix

import os
import sys
import zipfile
from tempfile import NamedTemporaryFile

from deployment.remote import exists, run, move, unzip, put, mkdir, phase_out, remove, which, normalize
from deployment.config import DeploymentConfig
from deployment.packaging import zipfiles, get_project_files, directory
from deployment.commands import pip, python, virtualenv

env.use_distribute = True
env.use_virtualenv = True
env.host_type = 'standalone'

PROJECT_FILES = [
    directory('api', filter='*.py'),
    directory('courses', filter='*.py'),
    directory('scheduler', filter='*.py'),
    directory('lib', 'csp', filter='*.py'),
    directory('lib', 'rpi_courses', filter='*.py'),
    directory('static', filter='*.*'),
    directory('templates', filter='*.*'),
    '__init__.py',
    'manage.py',
    'requirements.txt',
    'settings.py',
    'urls.py',
]

DEPLOY_FILE = os.path.join('deployment', 'deploy.json')

deploy_config = None

def staging():
    "Performs actions on the staging servers, as defined in deploy.json."
    global deploy_config
    deploy_config = DeploymentConfig(DEPLOY_FILE, 'staging').assign_to_env(env)

def production():
    "Performs actions on the production servers, as defined in deploy.json."
    global deploy_config
    deploy_config = DeploymentConfig(DEPLOY_FILE, 'production').assign_to_env(env)

def webfaction():
    global pip
    wf_root = normalize(deploy_config.project_root, '..')
    pip = pip.extend(tail_args=[
        '--install-option="--install-scripts=%s/bin"' % wf_root,
        '--install-option="--install-lib=%s/lib/python2.7"' % wf_root,
    ])

    env.use_distribute = False
    env.use_virtualenv = False

    #mkdir('~/tmp', recursive=True)


#@roles('webservers', 'databases', 'clock', 'workers')
def new_deploy():
    "Performs the set up of a first deployment, installed all the required software."
    pass

#@roles('webservers', 'databases', 'clock', 'workers')
def deploy():
    "Performs updates to servers to update the code bases."
    upload_project()
    migrate_db()

def activate_virtualenv_cmd():
    return 'source %s/bin/activate' % deploy_config.virtualenv_name

@roles('webservers')
def test():
    if which('pip-2.7'):
        print "PIP is installed"

@roles('webservers')
def upload_project():
    "Uploads the django project to the server."
    project_files = get_project_files(os.path.abspath('.'), PROJECT_FILES)
    tmp_file = NamedTemporaryFile()

    # package for the server and upload it
    zipfiles(project_files, to=tmp_file.name, root=os.path.abspath('.'))

    if not exists(deploy_config.project_root, '..'):
        mkdir(deploy_config.project_root, '..')

    put(tmp_file.name, (deploy_config.project_root, '..', 'project.zip'))

    # extract into location.

    with phase_out(deploy_config.project_root) as backup:
        if backup.exists:
            mkdir(deploy_config.project_root, recursive=True)

        move(
            (deploy_config.project_root, '..', 'project.zip'),
            (deploy_config.project_root, 'project.zip')
        )

        unzip(deploy_config.project_root, 'project.zip', delete=True)

        # upload settings.py for staging?

        backup.delete()

@roles('webservers')
def setup_environment():
    global virtualenv
    with cd(deploy_config.project_root):

        if env.use_distribute:
            if env.use_virtualenv:
                virtualenv = virtualenv.extend(['--distribute'])
            pip.install('distribute')

        if exists(deploy_config.virtualenv_name):
            remove(deploy_config.virtualenv_name, recursive=True, force=True)
        
        if env.use_virtualenv:
            virtualenv('--no-site-packages', deploy_config.virtualenv_name)

        # TODO: remove when not in debug
        if not exists('logs'):
            mkdir('logs')

        update_environment()


@roles('webservers')
def update_environment():
    with cd(deploy_config.project_root):
        if env.use_virtualenv:
            pip.install(r='requirements.txt', E=deploy_config.virtualenv_name)

            with prefix(activate_virtualenv_cmd()):
                run('python', 'manage.py', 'syncdb')
                run('python', 'manage.py', 'migrate')
        else:
            pip.install(r='requirements.txt')
    migrate_db()

@roles('webservers')
def migrate_db():
    with cd(deploy_config.project_root):
        manage_py = python.extend(['manage.py'])
        manage_py.syncdb()
        manage_py.migrate()

