#!/bin/bash

#####################################################################
# ONLY SUPPORT UBUNTU(maybe along with debian?)
#####################################################################


# install pgsql
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install postgresql

# exec sql
/etc/init.d/postgresql start
cp ./init.sql /tmp/init.sql
sudo su postgres -c 'psql -d db_zynb -f /tmp/init.sql'

# install python3-pip
sudo apt -y install python3.9
sudo apt -y install python3-pip

# install poetry
# sudo curl -sSL https://install.python-poetry.org | python3 -
sudo pip install poetry

# poetry init dependencies
poetry cache clear --all pypi -n
poetry install

mv RENAME_THIS_FILE_TO_.env.dev .env.dev