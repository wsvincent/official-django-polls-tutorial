#!/bin/sh
set -eu

if [ -x .venv/bin/python ]; then
    .venv/bin/python manage.py check --deploy --fail-level WARNING
    exec .venv/bin/python manage.py migrate --noinput
fi

python manage.py check --deploy --fail-level WARNING
exec python manage.py migrate --noinput
