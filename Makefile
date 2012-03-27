### configurable vars ###
APPS=api courses courses_viz scheduler jslog

# Requirements file to use
DEPLOY_REQUIREMENTS=requirements/deployment.txt
DEV_REQUIREMENTS=requirements/development.txt
# override
REQUIREMENTS=

DEPLOY=$(APPS) lib requirements yacs manage.py Makefile

# certain commands accept arguments
ARGS=

# force pip to upgrade all packages
FORCE_UPGRADE=

# where collectstatic puts its files
STATIC_CACHE=yacs/static/root

# executables
PYTHON := `which python`
PYTHON_VERSION=
NOSETESTS := `which nosetests`
PIP := `which pip`
VIRTUALENV := `which virtualenv`

PIP_ARGS=

# syncing operations for git
# usually you put the appropriate database driver here
PRODUCTION_SETTINGS=yacs/settings/test.json
PRODUCTION_REQUIREMENTS=requirements/postgresql.txt
PRODUCTION_USE_VIRTUALENV=1
PRODUCTION_VIRTUALENV_NAME=yacs_env
PRODUCTION_VIRTUALENV_LOCATION=~/
TEMP_ARCHIVE_NAME=yacs_project_deploy_archive
PRODUCTION_ROOT=~/
PRODUCTION_DIR_NAME=yacs-test
PRODUCTION_SERVER=hui.afraid.org
PRODUCTION_PRE_COMMAND=source .bashrc; source .bash_profile;
# this is automatically defined when deploying to remote server
#PRODUCTION=

help:
	@echo "Commands supported:"
	@echo "  bootstrap             Sets up development environment."
	@echo "  clean                 Removes all python bytecode files and collected static files."
	@echo "  deploy                Deploys to a given remote server given the variables in this Makefile. Uses update_environment."
	@echo "  docs                  Builds sphinx documentation."
	@echo "  loc                   Returns an estimated number of lines of code."
	@echo "  perform_data_refresh  Performs cron job tasks for all data on the remote server."
	@echo "  remove_backup         Removes the backup folder from a deploy. Use after deploying."
	@echo "  restore_backup        Restores backup folder from a deploy. Used to undo a deploy."
	@echo "  test                  Runs all unit tests and generate a coverage report."
	@echo "  test_django           Test only YACS's django apps. No coverage."
	@echo "  test_lib              Test only YACS's lib directory. No coverage."
	@echo "  test_only             Runs all unit tests without coverage."
	@echo "  update_environment    Updates the environment dependencies and caches for deployment."
	@echo "  scss                  Runs sass file watcher to convert scss files into css."

##### simple commands #####

bootstrap: REQUIREMENTS=$(DEV_REQUIREMENTS)
bootstrap: install_requirements

loc:
	find -E . -iregex ".+/[^0][^/]+\.(py|html|js|scss|txt)$$" -not -iregex ".+/(_build|test_reports)/.+" -not -name "manage.py" | xargs wc -l

docs:
	echo "Generating documentation ..."
	(cd docs && make html)

scss:
	sass --watch yacs/static/global/scss:yacs/static/global/css

clean:
	@echo "Removing all *.pyc files."
	find . -name "*.pyc" | xargs rm
	@echo "Removing all *.pyo files."
	find . -name "*.pyo" | xargs rm
	# python 3
	@echo "Removing all __pycache__ directories."
	find . -name "__pycache__" -type directory | xargs rm -r
	# django
	@echo "Removing collected static files."
	rm -r $(STATIC_CACHE)
	# deployment
	@echo "Removing deployment cruft"
	rm -f $(TEMP_ARCHIVE_NAME).tar.gz $(TEMP_ARCHIVE_NAME).tar

##### END simple commands #####

##### remote commands - intended for server operation #####

PRODUCTION_FULLPATH=$(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)
CD_PROJECT=cd $(PRODUCTION_FULLPATH)

remote = \
	  ssh $(PRODUCTION_SERVER) "$(PRODUCTION_PRE_COMMAND)$(1)"

ifdef PRODUCTION_USE_VIRTUALENV
USE_VIRTUALENV := source $(PRODUCTION_VIRTUALENV_LOCATION)/$(PRODUCTION_VIRTUALENV_NAME)/bin/activate && export YACS_ENV=production && 
else
USE_VIRTUALENV=
endif

WF_remove_backup: override PRODUCTION_DIR_NAME=yacs
WF_remove_backup: override PRODUCTION_ROOT=~/webapps/yacs
WF_remove_backup: override PRODUCTION_ROOT=~/webapps/yacs

WF_restart: override PRODUCTION_DIR_NAME=yacs
WF_restart: override PRODUCTION_ROOT=~/webapps/yacs
WF_restart:
	$(call remote,$(CD_PROJECT) && $(PRODUCTION_FULLPATH)/../apache2/bin/restart)

WF_deploy: override PRODUCTION_USE_VIRTUALENV=
WF_deploy: override PRODUCTION_USE_VIRTUALENV=
WF_deploy: override USE_VIRTUALENV=
WF_deploy: override PRODUCTION_DIR_NAME=yacs
WF_deploy: override PRODUCTION_ROOT=~/webapps/yacs
WF_deploy: override PYTHON_VERSION=2.7
WF_deploy: override PRODUCTION_SETTINGS=yacs/settings/staging.json
WF_deploy: \
	PIP_ARGS+=--install-option="--install-scripts=$(PRODUCTION_FULLPATH)/bin/" \
	--install-option="--install-lib=$(PRODUCTION_FULLPATH)/lib/python2.7"

WF_deploy deploy: backup_current create_tarball upload_and_extract_tarball remove_tarball
	# set up virtualenv
ifdef PRODUCTION_VIRTUALENV
	$(call remote,$(CD_PROJECT) && make create_virtualenv PRODUCTION=1)
endif
	# install appropriate database drivers
ifdef PRODUCTION_REQUIREMENTS
	$(call remote,$(CD_PROJECT) && $(USE_VIRTUALENV) make install_requirements PRODUCTION=1 REQUIREMENTS=$(PRODUCTION_REQUIREMENTS))
endif
	# update production settings
	$(call remote,$(CD_PROJECT) && rm -f $(PRODUCTION_FULLPATH)/yacs/settings/*.json)
	scp $(PRODUCTION_SETTINGS) $(PRODUCTION_SERVER):$(PRODUCTION_FULLPATH)/yacs/settings/production.json
	# perform regular pip install, syncdb, migrate, collectstatic
	$(call remote,$(CD_PROJECT) && $(USE_VIRTUALENV) make update_environment PRODUCTION=1 PIP_ARGS='$(PIP_ARGS)' PYTHON_VERSION=$(PYTHON_VERSION))

perform_data_refresh:
	$(call remote,$(CD_PROJECT) && $(USE_VIRTUALENV) make refresh_data PRODUCTION=1 PIP_ARGS='$(PIP_ARGS)' PYTHON_VERSION=$(PYTHON_VERSION))

create_tarball: remove_tarball
	tar -cf $(TEMP_ARCHIVE_NAME).tar --exclude="*.pyc" --exclude="__pycache__" --exclude="*.pyo" --exclude=".*" $(DEPLOY)
	gzip -9 $(TEMP_ARCHIVE_NAME).tar

remove_tarball:
	rm -f $(TEMP_ARCHIVE_NAME).tar $(TEMP_ARCHIVE_NAME).tar.gz

backup_current:
	$(call remote,mkdir -p $(PRODUCTION_FULLPATH) && mv -f $(PRODUCTION_FULLPATH) $(PRODUCTION_FULLPATH)_tmp)

restore_backup:
	$(call remote,mkdir -p $(PRODUCTION_FULLPATH)_tmp && mv -f $(PRODUCTION_FULLPATH)_tmp $(PRODUCTION_FULLPATH))

WF_remove_backup remove_backup:
	$(call remote,rm -rf $(PRODUCTION_FULLPATH)_tmp)

upload_and_extract_tarball:
	@echo "Creating directory"
	$(call remote,mkdir -p $(PRODUCTION_FULLPATH))
	@echo "Uploading repo"
	scp $(TEMP_ARCHIVE_NAME).tar.gz $(PRODUCTION_SERVER):$(PRODUCTION_FULLPATH)
	@echo "Extracting repository and bootstrapping..."
	$(call remote,$(CD_PROJECT) && tar -zxvf $(TEMP_ARCHIVE_NAME).tar.gz)

# commands run locally (by the deployment server)

create_virtualenv:
ifneq ($(strip $(PRODUCTION_USE_VIRTUALENV)),)
ifdef PRODUCTION
	cd $(PRODUCTION_VIRTUALENV_LOCATION) && $(VIRTUALENV) $(PRODUCTION_VIRTUALENV_NAME)
endif
endif

update_environment: REQUIREMENTS=$(DEPLOY_REQUIREMENTS)
update_environment: install_requirements syncdb collectstatic

install_requirements:
ifneq ("$(FORCE_UPGRADE)", "")
	$(PIP) install -r $(REQUIREMENTS) --upgrade $(PIP_ARGS)
else
	$(PIP) install -r $(REQUIREMENTS) $(PIP_ARGS)
endif

ifdef PRODUCTION
PYTHON_EXEC = export YACS_ENV=production && $(PYTHON)$(PYTHON_VERSION)
else
PYTHON_EXEC = $(PYTHON)$(PYTHON_VERSION)
endif

syncdb:
	$(PYTHON_EXEC) manage.py syncdb --noinput
	$(PYTHON_EXEC) manage.py migrate

collectstatic:
	$(PYTHON_EXEC) manage.py collectstatic --noinput

refresh_data: update_courses create_section_cache create_robots_txt

update_courses:
	$(PYTHON_EXEC) manage.py import_course_data $(ARGS)

create_robots_txt:
	$(PYTHON_EXEC) manage.py sync_robots_data $(ARGS)

create_section_cache:
	$(PYTHON_EXEC) manage.py create_section_cache

##### END remote commands #####

##### Testing Operations #####

test: prefix=coverage run -a 
# we can't run with python arg
test: PYTHON=
test: begin_coverage test_only end_coverage
test_only: test_django test_lib pep8

begin_coverage:
	coverage erase

end_coverage:
	coverage html

test_django:
	$(prefix)$(PYTHON_EXEC) manage.py test --failfast $(APPS)

test_lib:
	$(prefix)$(NOSETESTS) -x -w lib

pep8:
	pep8 . --exclude=migrations --statistics --count --ignore=E501

##### END Testing Operations #####

