#!/bin/sh
set -eu

if [ -x .venv/bin/python ]; then
    exec .venv/bin/python manage.py migrate --noinput
fi

exec python manage.py migrate --noinput
