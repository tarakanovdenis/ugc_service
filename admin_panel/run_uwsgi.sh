#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

python /opt/app/manage.py collectstatic --no-input
python /opt/app/manage.py makemigrations --no-input
python /opt/app/manage.py migrate --no-input

uwsgi --strict --ini /opt/app/uwsgi/uwsgi.ini

