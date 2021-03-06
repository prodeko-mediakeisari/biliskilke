#!/usr/bin/env bash

apt-get update
# Required for add-apt-repository
apt-get install -y software-properties-common python-software-properties

# Add required repositories
# node.js
add-apt-repository -y ppa:chris-lea/node.js >> /tmp/add-apt-errors 2>&1
# python3.3
add-apt-repository -y ppa:fkrull/deadsnakes >> /tmp/add-apt-errors 2>&1

# download the package lists from the repositories
apt-get update


# --- miscellaneous ----

apt-get install -y curl git-core screen vim

# --- python ---

# install python3.3
apt-get install -y python3.3

# set default python version to 3.3
ln -sf /usr/bin/python3.3 /usr/bin/python
dpkg --configure python

# install setuptools
curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -o - | sudo python

# install pip using setuptools
easy_install pip

# Set default pip to 3.3
ln -sf /usr/local/bin/pip3.3 /usr/bin/pip


# --- apache ---

# install packages
apt-get install -y apache2 libapache2-mod-wsgi

# remove default webroot
rm -rf /var/www

# symlink project as webroot
ln -fs /vagrant /var/www

# setup hosts file
VHOST=$(cat <<EOF
<VirtualHost *:80>
  DocumentRoot "/vagrant"
  ServerName localhost
  <Directory /vagrant>
    AllowOverride All
    Order Allow,Deny
    Allow From All
  </Directory>
</VirtualHost>
EOF
)
echo "${VHOST}" > /etc/apache2/sites-available/default

# enable apache rewrite module
a2enmod rewrite


# --- mysql ---

# install packages
echo mysql-server mysql-server/root_password select "vagrant" | debconf-set-selections
echo mysql-server mysql-server/root_password_again select "vagrant" | debconf-set-selections
apt-get install -y mysql-server-5.5 libmysqlclient-dev

# create database
mysql -uroot -pvagrant -e "CREATE USER 'bilis'@'localhost' IDENTIFIED BY 'bilis';"
mysql -uroot -pvagrant -e "GRANT ALL PRIVILEGES on *.* TO 'bilis'@'localhost';"
mysql -uroot -pvagrant -e "CREATE DATABASE bilis;"


# --- node.js ---

# install node.js and dependencies
apt-get install -y g++ make nodejs

# install npm packages
npm install -g less
npm install -g yuglify


# --- Required python modules ---
pip install -r /vagrant/requirements.txt

# tasks
cd /vagrant && python manage.py syncdb --noinput
cd /vagrant && python manage.py migrate
cd /vagrant && python manage.py createcachetable bilis_cache

# Run server and static file watcher in screen
su - vagrant -c "cd /vagrant && screen -S server -d -m python manage.py runserver 0.0.0.0:8000"
su - vagrant -c "cd /vagrant && screen -S watcher -d -m python manage.py watchstatic"

# --- restart apache ---

service apache2 restart
