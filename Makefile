### configurable vars ###
APPS=api courses scheduler

# Requirements file to use
DEPLOY_REQUIREMENTS=requirements/deployment.txt
DEV_REQUIREMENTS=requirements/development.txt
# override
REQUIREMENTS=

DEPLOY=api courses scheduler lib requirements yacs manage.py Makefile

# certain commands accept arguments
ARGS=

# force pip to upgrade all packages
FORCE_UPGRADE=

# where collectstatic puts its files
STATIC_CACHE=yacs/static/root

# executables
PYTHON := `which python`
NOSETESTS := `which nosetests`
PIP := `which pip`
VIRTUALENV := `which virtualenv`

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
	echo "Removing all *.pyc files."
	find . -name "*.pyc" | xargs rm
	echo "Removing all *.pyo files."
	find . -name "*.pyo" | xargs rm
	# python 3
	echo "Removing all __pycache__ directories."
	find . -name "__pycache__" -type directory | xargs rm -r
	# django
	echo "Removing collected static files."
	rm -r $(STATIC_CACHE)
	# deployment
	echo "Removing deployment cruft"
	rm -f $(TEMP_ARCHIVE_NAME).tar.gz $(TEMP_ARCHIVE_NAME).tar

##### END simple commands #####

##### remote commands - intended for server operation #####

CD_PROJECT := cd $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)

remote = \
	  ssh $(PRODUCTION_SERVER) "$(1)"

ifdef PRODUCTION_USE_VIRTUALENV
USE_VIRTUALENV := source $(PRODUCTION_VIRTUALENV_LOCATION)/$(PRODUCTION_VIRTUALENV_NAME)/bin/activate && export YACS_ENV=production && 
else
USE_VIRTUALENV=
endif

deploy: backup_current create_tarball upload_and_extract_tarball remove_tarball
	# install appropriate database drivers
	$(call remote,$(CD_PROJECT) && make create_virtualenv PRODUCTION=1 && $(USE_VIRTUALENV) make install_requirements PRODUCTION=1 REQUIREMENTS=$(PRODUCTION_REQUIREMENTS))
	# update production settings
	$(call remote,$(CD_PROJECT) && rm -f $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)/yacs/settings/*.json)
	scp $(PRODUCTION_SETTINGS) $(PRODUCTION_SERVER):$(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)/yacs/settings/production.json
	# perform regular pip install, syncdb, migrate, collectstatic
	$(call remote,$(CD_PROJECT) && $(USE_VIRTUALENV) make update_environment PRODUCTION=1)

perform_data_refresh:
	$(call remote,$(CD_PROJECT) && $(USE_VIRTUALENV) make refresh_data PRODUCTION=1)

create_tarball: remove_tarball
	tar -cf $(TEMP_ARCHIVE_NAME).tar --exclude="*.pyc" --exclude="__pycache__" --exclude="*.pyo" --exclude=".*" $(DEPLOY)
	gzip -9 $(TEMP_ARCHIVE_NAME).tar

remove_tarball:
	rm -f $(TEMP_ARCHIVE_NAME).tar $(TEMP_ARCHIVE_NAME).tar.gz

backup_current: remove_backup
	$(call remote,mkdir -p $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME) && mv -f $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME) $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)_tmp)

restore_backup:
	$(call remote,mkdir -p $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)_tmp && mv -f $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)_tmp $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME))

remove_backup:
	$(call remote,rm -rf $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)_tmp)

upload_and_extract_tarball:
	@echo "Creating directory"
	$(call remote,mkdir -p $(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME))
	@echo "Uploading repo"
	scp $(TEMP_ARCHIVE_NAME).tar.gz $(PRODUCTION_SERVER):$(PRODUCTION_ROOT)/$(PRODUCTION_DIR_NAME)
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
	$(PIP) install -r $(REQUIREMENTS) --upgrade
else
	$(PIP) install -r $(REQUIREMENTS)
endif

syncdb:
	$(PYTHON) manage.py syncdb --noinput
	$(PYTHON) manage.py migrate

collectstatic:
	$(PYTHON) manage.py collectstatic --noinput

refresh_data: update_courses create_section_cache create_robots_txt

update_courses:
	$(PYTHON) manage.py import_course_data $(ARGS)

create_robots_txt:
	$(PYTHON) manage.py sync_robots_data $(ARGS)

create_section_cache:
	$(PYTHON) manage.py create_section_cache

##### END remote commands #####

##### Testing Operations #####

test: prefix=coverage run -a 
# we can't run with python arg
test: PYTHON=
test: begin_coverage test_only end_coverage
test_only: test_django test_lib

begin_coverage:
	coverage erase

end_coverage:
	coverage html

test_django:
	$(prefix)$(PYTHON) manage.py test --failfast $(APPS)

test_lib:
	$(prefix)$(NOSETESTS) -x -w lib

##### END Testing Operations #####

