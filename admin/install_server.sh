#!/bin/sh
# Dunya server environment for dev setup

echo "---------------------------------------------"
echo "installing some requirements with apt-get "
echo "---------------------------------------------"

apt-get update
apt-get -y upgrade

apt-get install -y python-virtualenv python-dev pxz git
apt-get install -y python-numpy python-scipy python-matplotlib libsndfile1-dev lame libjpeg8-dev postgresql-server-dev-all libxml2-dev libxslt1-dev
apt-get install -y build-essential libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev python-dev libsamplerate0-dev libtag1-dev python-numpy-dev

apt-get install -y node-less

echo "---------------------------------------------"
echo "Installing PostgreSQL"
echo "---------------------------------------------"

# Setting up PostgreSQL
PG_VERSION=9.3

apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" "postgresql-server-dev-$PG_VERSION"
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Setting up PostgreSQL access
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
sed -i "s/local\s*all\s*all\s*peer/local all all trust/" "$PG_HBA"
echo "host all all all trust" >> "$PG_HBA"

# Explicitly set default client_encoding
echo "client_encoding = utf8" >> "$PG_CONF"

service postgresql restart

echo "---------------------------------------------"
echo "Installing with PIP some requirements"
echo "---------------------------------------------"

# Setting up the application
cd /vagrant/
pip install --upgrade setuptools
pip install python-dateutil
pip install --allow-external eyed3 --allow-unverified eyed3 eyed3 
pip install Django==1.8b2
pip install -r requirements

echo "---------------------------------------------"
echo "Create database and tables "
echo "---------------------------------------------"
sudo adduser \
   --system \
   --shell /bin/bash \
   --gecos 'User for managing of git version control' \
   --group \
   --disabled-password \
   --home /home/dunya \
   dunya
sudo -u postgres psql -c "CREATE USER dunya SUPERUSER;"
sudo -u postgres psql -c "create database \"dunya\""
sudo -u postgres psql -c "create extension unaccent;"

# If you want to create an empty database, uncomment this line: 
#fab setupdb