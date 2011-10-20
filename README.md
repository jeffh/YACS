# YACS
Sane Course Scheduling.

YACS is a web-based course schedule with an emphasis on usability. It is also flexible enough to work with other school course data.

by Jeff Hui.
Send questions and comments to [@jeffhui][] / huij@rpi.edu.

[@jeffhui]: http://twitter.com/jeffhui "Twitter: @jeffhui"

## Setup
YACS is actively developed on Python 2.7. So go get that installed first. As good python practice, you should put this project inside a virtualenv, but that's not covered here.

You can download an archive from the top-right of the github page or clone the repo:

    git clone git://github.com/jeffh/YACS.git

Which will download code into a YACS folder where you run this command.

1. Install [Postgres][postgres]. Last time I checked, SQLite was too slow even for development.
2. Install [distribute][distribute] or [setuptools][setuptools] which PIP depends on. If you have the easy_install command, you have setuptools installed. To install distribute, do:

    ```
    wget http://python-distribute.org/distribute_setup.py
    python distribute_setup.py
    rm distribute_setup.py
    ```

3. Install [pip][]:

    ```
    wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py
    rm get-pip.py
    ```

4. Using pip, you can automatically install all the other dependencies by doing:

    `pip install -r dev_requirements.txt`

    And pip should do the rest! If you get errors for psycopg2, you can install that manually and remove it from dev_requirements.txt before re-running the command above.

5. Edit settings/overrides.py to point to your settings for your PostgreSQL database.

5. CD into the project and run the following to set up the database:

    ```
    python manage.py syncdb
    python manage.py migrate
    ```

When calling syncdb, you'll be ask to create a superuser, it is purely optional, only the debug-toolbar is visible for logged in super-users.

6. Run this command to import the course data from RPI:

    `python manage.py import_course_data`

7. Run the dev server using: `python manage.py runserver`

8. Point your browser to [http://localhost:8000/][local] and viola!
9. ???
10. Profit?

[postgres]: http://www.postgresql.org/ "PostgreSQL"
[pip]: http://www.pip-installer.org/en/latest/index.html
[distribute]: http://pypi.python.org/pypi/distribute
[setuptools]: http://pypi.python.org/pypi/setuptools
[local]: http://localhost:8000/

## Project layout
Currently the project is laid out as follows:

- **api**: The old api application based on Piston. Deprecated and soon to be removed because of the vague errors when debugging this app caused by Piston.
- **courses**: The courses application. Contains the schema and manages the storage of course data.
- **deployment**: Some deployment code helper. Not ready for prime-time.
- **lib**: Contains library code that can, be potentially, separated into an independent project. To enforce this separability, this folder is added to the sys.path for absolute imports
- **newapi**: This new api application is here. Piggy-backs the majority of its code from courses to generate the API output.
- **scheduler**: This app handles course scheduling. Relies on the courses app for all the course data.
- **selenium_tests**: Where all selenium tests reside
- **settings**: Project settings folder (unlike normal Django projects). Partitioned into separate files for easier deployments.
- **static**: Where all static media resides (js, css, imgs, sass, etc.)
- **templates**: Where all the templates are for this project. This is used for displaying all the pages.
- **dev_requirements.txt**: All the required dependencies for development
- **requirements.txt**: All the required dependencies for deployment. May be deprecated in favor of just using dev_requirements.txt
- **fabfile.py**: Configuration for Fabric. Like a Makefile or Rakefile.
- **management.py**: Django's CLI.
- **urls.py**: Where all the incoming URLs are routed to.

## Fabric Commands
Fabric is a python-variant of make or rake. When installing using dev_requirements.txt, it got installed.

There are some pretty nice commands you can view by doing:

    fab -l  # that's an L

But many of these don't quite work (very environment specific), the ones that are safe to use are listed here:

- **fab test** - Runs all unit tests for this project. But sometimes there are stale python object files (pyc or pyo), so use…
- **fab clean** - Removes all pyc, pyo and pycache files.
- **fab loc** - A nice shortcut to get the general line of code count. This does not include some json files in the templates dir. Makes me cry everytime to see how large this number is.
- **fab scss** - A shortcut for running [Sass][sass]. *Sass must be installed manually*.

[sass]: http://sass-lang.com/

## Help
This project is still evolving. There are still issues to tackle. Go to the [GitHub issues][issues] page to see them all.

[issues]: https://github.com/jeffh/YACS/issues