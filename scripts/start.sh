#!/bin/sh
set -eu

if [ -x .venv/bin/gunicorn ]; then
    exec .venv/bin/gunicorn mysite.wsgi:application --config gunicorn.conf.py
fi

exec gunicorn mysite.wsgi:application --config gunicorn.conf.py
