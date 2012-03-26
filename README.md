# YACS [![Build Status](https://secure.travis-ci.org/jeffh/YACS.png?branch=master)](http://travis-ci.org/jeffh/YACS)
Simple, Sane Course Scheduling.

YACS is a web-based course schedule with an emphasis on usability.
It is also flexible enough to work with other school course data.

Send questions and comments to [@jeffhui][] or huij@rpi.edu.

If you're an RPI student and just want to use it. Go to [yacs.me][yacsme]

[@jeffhui]: http://twitter.com/jeffhui "Twitter: @jeffhui"
[yacsme]: http://yacs.me/ "YACS - The usable online course scheduler"

## Setup
YACS is actively developed on [Python][] 2.7. So go get that installed first.
It's good python practice to put this project inside a [virtualenv][],
but that's beyond the scope of this README.

You can download an archive from the top-right of the github page or clone the repo:

    git clone git://github.com/jeffh/YACS.git

Which will download code into a YACS folder where you run this command.

[Python]: http://python.org/
[virtualenv]: http://www.virtualenv.org/en/latest/index.html

### Dependencies

YACS is built on top of [Django][] 1.4rc1. Thus, it requires a database driver to run.
Install the appropriate driver and its database, or just use the bundled SQLite.

[Django]: https://www.djangoproject.com/ "Django Web Framework"

### Setup (Development)

1. YACS uses a lot of dependencies. It relies on [pip][] to install them. Simply do:
    `pip install -r requirements/development.txt`
   Which will install all the dependencies YACS needs (minus the database driver).


2. Edit `s.DATABASES` variable in the `yacs/settings/development.py` file to your
   appropriate database settings.

3. Run the following commands. When calling syncdb, you'll be ask to create a superuser,
   it is purely optional, only the debug-toolbar is visible for logged in super-users.

    ```
    python manage.py syncdb
    python manage.py migrate
    ```

4. Next we need to get some data. Run these commands to import the course data from RPI
   (These will take awhile).

    ```
    python manage.py import_course_data
    python manage.py import_catalog_data
    ```

5. Check it out by running the dev server `python manage.py runserver` and pointing your
   browser to [http://localhost:8000/][local] and viola!

6. (Optional) If you plan on editing the CSS. YACS uses [SASS][] to generate the CSS.
   You'll have to install that. Once you have, use `make scss` to make sass
   automatically update the stylesheets as you change them.

7. ???
8. Profit?

[SASS]: http://sass-lang.com/
[pip]: http://www.pip-installer.org/en/latest/index.html
[local]: http://localhost:8000/

## Project layout
Currently the project is laid out as follows:

- **api**: API application. Where all  API related code is. Relies on courses and scheduler app.
- **courses**: The courses application. Contains the schema and manages the storage of course data. Also contains course-data-displaying views.
- **courses_viz**: An application that stores visualization of course data. (Part of Introduction to Visualization class)
- **jslog**: An application that can record basic JS data for debugging.
- **lib**: Contains library code that can, be potentially, separated into an independent project. To enforce this separability, this folder is added to the sys.path for absolute imports
- **scheduler**: This app handles course scheduling. Relies on the courses app for all the course data.
- **yacs**: Project files. Contains settings, root urls, templates, static files, etc.
- **test_reports**: Only appears when tests are executed. Used to see the test coverage.
- **requirements**: Contains various requirement files for PIP.
- **Makefile**: Used for running tests, cleaning python caches and deployment.
- **manage.py**: Django's CLI.

## Help
This project is still evolving. There are still issues to tackle. Go to the [GitHub issues][issues] page to see them all.

[issues]: https://github.com/jeffh/YACS/issues
