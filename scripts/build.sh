#!/bin/sh
set -eu

uv sync --locked --no-dev --compile-bytecode
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py check --deploy --fail-level WARNING
