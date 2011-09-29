from fabric.api import roles, env, local
from fabric.context_managers import cd, prefix, lcd
from fabric.contrib.files import upload_template

import os
import sys
import zipfile
from tempfile import NamedTemporaryFile

from deployment.remote import exists, run, move, unzip, put, mkdir, phase_out, remove, which, normalize
from deployment.config import DeploymentConfig
from deployment.packaging import zipfiles, get_project_files, directory
from deployment.commands import Command

aptget = Command('apt-get', sudo=True)
python = Command('python2.7',
    sudo_install=lambda *_: aptget.install('-y', 'python-all')
)
pip = Command('pip-2.7',
    install=lambda *_: run('curl', 'https://raw.github.com/pypa/pip/master/contrib/get-pip.py', '|',
        python.path, '-')
)
virtualenv = Command('virtualenv',
    install=lambda *_: pip.install('virtualenv')
)


env.use_distribute = True
env.use_virtualenv = True
env.apache_restart = ('apache2', 'restart')

PROJECT_FILES = [
    directory('api', filter='*.py'),
    directory('courses', filter='*.py'),
    directory('scheduler', filter='*.py'),
    directory('lib', 'csp', filter='*.py'),
    directory('lib', 'rpi_courses', filter='*.py'),
    directory('static', filter='*.*'),
    directory('templates', filter='*.*'),
    directory('settings', filter='*.py'),
    '__init__.py',
    'manage.py',
    'requirements.txt',
    'urls.py',
]
TEMPLATES = {
    normalize('settings', 'database_template.py'): normalize('settings', 'database.py')
}

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
    env.apache_restart = ('%s/apache2/bin/restart' % wf_root, )

    #mkdir('~/tmp', recursive=True)

def scss():
    "Watches sass files to convert to css"
    local('sass --watch static/global/scss:static/global/css')

def test(app=None):
    """Returns all tests in lib and custom django apps. Optionally accepts specific apps to test.
    If lib is provided as app, only the lib directory is tested.
    """
    if app is not None:
        if app == 'lib':
            with lcd('lib'):
                local('nosetests')
            return
        local('python manage.py test --failfast ' + app)
        return
    local('python manage.py test --failfast api courses scheduler')
    with lcd('lib'):
        local('nosetests')
    return

def loc():
    "Returns the number of lines of all source files, excluding migrations."
    local('find -E . -iregex ".+/[^0][^/]+\.(py|html|json)$" | xargs wc -l')

@roles('webservers')
def new_deploy():
    "Performs the set up of a first deployment, installed all the required software."
    pass

@roles('webservers')
def deploy(use_pip=False):
    "Performs updates to servers to update the code bases."
    upload_project()
    update_environment(use_pip)
    restart()

def activate_virtualenv_cmd():
    return 'source %s/bin/activate' % deploy_config.virtualenv_name

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

        mkdir((deploy_config.project_root, 'logs'))

        # upload settings.py for staging?
        upload_templates()

        backup.delete()

@roles('webservers')
def upload_templates():
    with cd(deploy_config.project_root):
        for src, dest in TEMPLATES.items():
            upload_template(src, dest, context=deploy_config.deployment_settings, use_jinja=True, backup=False)

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
def update_environment(use_pip=False):
    use_pip = bool(int(use_pip))
    with cd(deploy_config.project_root):
        if env.use_virtualenv:
            if use_pip:
                pip.install(r='requirements.txt', E=deploy_config.virtualenv_name)

            with prefix(activate_virtualenv_cmd()):
                run('python', 'manage.py', 'syncdb')
                run('python', 'manage.py', 'migrate')
        else:
            if use_pip:
                pip.install(r='requirements.txt')

            manage_py = python.extend(['manage.py'])
            manage_py.syncdb()
            manage_py.migrate()

@roles('webservers')
def restart():
    run(*env.apache_restart)

