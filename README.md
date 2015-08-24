# Prerequisites
* django: easy_install django
* bower: npm install -g bower
* django-bower: pip install django-bower
* mysqldb: apt-get install python2.7-mysqldb
* python-dateutil: apt-get install python-dateutil

# Installation
* copy propertymanagementtools/database.conf.sample to propertymanagementtools/database.conf and put in values for your db instance
* generate sample data: ./manage.py generatedata
* run the server: ./manage.py runserver 192.168.0.123:4567
* log in to the superuser: username = superuser , password = superpass
* install bower packages: ./manage.py bower install

