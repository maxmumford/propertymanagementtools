# Prerequisites
* pip install django
* npm install -g bower
* pip install django-bower
* sudo apt-get install python2.7-mysqldb
* sudo apt-get install python-dateutil
* sudo apt-get install python-simplejson
* sudo pip install django-tables2
* sudo pip install django-bootstrap3
* sudo pip install eadred
* sudo apt-get install nodejs
* sudo ln -s /usr/bin/nodejs /usr/bin/node

# Installation
* cp propertymanagementtools/database.conf.sample propertymanagementtools/database.conf
* vi propertymanagementtools/database.conf
* ./manage.py bower install
* ./manage.py generatedata
* ./manage.py runserver 192.168.0.123:4567
* log in to the superuser: username = superuser , password = superpass
