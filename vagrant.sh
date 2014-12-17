#!/bin/sh

# install external dependency
sudo pacman -Sy --noconfirm --needed postgresql libmemcached python2-pip

# setup virtualenv
pip2 install pew --user
PATH=$HOME/.local/bin:$PATH
export WORKON_HOME=$HOME/.pew
pew new -r /vagrant/requirements.txt -d yacs

# setup PATH
touch ~/.profile
sed -i '$a\
\
# pip user scheme PATH\
PATH="$HOME/.local/bin:$PATH"\
\
# pew virtualenv dir\
export WORKON_HOME=$HOME/.pew
' ~/.profile

# setup postgresql
sudo su -c "pg_ctl -D ~/data initdb" postgres
sudo systemctl start postgresql
sudo su postgres <<EOF
createdb yacsdb
psql -c 'CREATE USER yacs' yacsdb
EOF

# setup project
(
cd /vagrant
pew-in yacs python manage.py migrate
pew-in yacs python manage.py import_course_data   # imports from RPI SIS + PDFs
pew-in yacs python manage.py import_catalog_data  # imports from RPI course catalog
pew-in yacs python manage.py create_section_cache # creates cache for generating schedules
psql -c "UPDATE courses_semester SET visible=TRUE WHERE id=1;" yacsdb yacs # make latest semester visible
)
