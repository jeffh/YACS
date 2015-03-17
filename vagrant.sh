#!/bin/sh

# update package managers
pacman -Sy --noconfirm pacman package-query
pacman-db-upgrade

# install external dependency
pacman -S --noconfirm --needed postgresql libmemcached python-pip

# setup postgresql
su -c "pg_ctl -D ~/data initdb" postgres
systemctl start postgresql
su postgres <<EOF
createdb yacsdb
psql -c 'CREATE USER yacs' yacsdb
EOF

# setup virtualenv
su vagrant <<EOF
yaourt -S --noconfirm python-pew

touch ~/.profile
sed -i '$a\
\
# pew virtualenv dir\
export WORKON_HOME=$HOME/.pew
' ~/.profile

EOF

# setup project
su vagrant <<EOF
pew new -p python2 -r /vagrant/requirements.txt -d yacs
EOF
