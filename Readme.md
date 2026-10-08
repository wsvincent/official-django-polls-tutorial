# Official Django Polls Tutorial Code

Source code for the [official Django Polls tutorial](https://docs.djangoproject.com/en/6.1/intro/), using Django 6.1 and Python 3.14.

The project follows tutorial parts 1–8, including Django Debug Toolbar. The polls templates share a page wrapper so the toolbar can appear on each page.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from the project directory on Windows, macOS, or Linux:

```sh
uv sync --locked
uv run manage.py migrate
uv run manage.py runserver
```

uv uses the Python 3.14 version pinned in `.python-version`, downloads it if needed, and creates `.venv` with the dependencies recorded in `uv.lock`. Open <http://127.0.0.1:8000/polls/> to view the application.

## Development

Django Debug Toolbar appears on HTML pages when browsing from localhost with `DEBUG = True`. It is installed with the development dependencies and disabled during tests. Click its handle on the right side of the page to inspect SQL queries, templates, and request details.

Run the tests and Django's system checks:

```sh
uv run manage.py test
uv run manage.py check
```

Black is included in the development dependencies:

```sh
uv run black .
```

Use `uv add <package>` for application dependencies and `uv add --dev <package>` for development tools. Commit both `pyproject.toml` and `uv.lock` after changing dependencies.

## Want Help Learning Django?
Check out [LearnDjango](https://learndjango.com) for dozens of free tutorials and premium courses to help you master web development with Python and Django.
