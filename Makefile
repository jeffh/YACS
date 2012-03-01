# configurable vars
APPS=api courses scheduler

# executables
PYTHON=`which python`
NOSETESTS=`which nosetests`

help:
	echo "Commands supported:"
	echo "  clean\tRemoves all *.pyc files"
	echo "  docs\tBuilds sphinx documentation."
	echo "  test\tRuns all unit tests and generate a coverage report."
	echo "  test_only\tRuns all unit tests without coverage."
	echo "  scss\tRuns sass file watcher to convert scss files into css."

##### simple commands #####

docs:
	echo "Generating documentation ..."
	(cd docs && make html)

scss:
	sass --watch static/global/scss:static/global/css

clean:
	echo "Removing all *.pyc files."
	find . -name "*.pyc" | xargs rm
	echo "Removing all *.pyo files."
	find . -name "*.pyo" | xargs rm
	echo "Removing all __pycache__ directories."
	find . -name "__pycache__" -type directory | xargs rm -r

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

