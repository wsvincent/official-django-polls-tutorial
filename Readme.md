# Official Django Polls Tutorial Code

Source code for the [official Django Polls tutorial](https://docs.djangoproject.com/en/6.1/intro/), using Django 6.1 and Python 3.14.

The project follows tutorial parts 1–8, including Django Debug Toolbar. The polls templates share a page wrapper so the toolbar can appear on each page.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from the project directory on Windows, macOS, or Linux:

Copy `.env.example` to `.env` first. The example enables local development with
SQLite; `.env` is ignored by Git. On macOS or Linux, run `cp .env.example .env`.
On PowerShell, run `Copy-Item .env.example .env`.

```sh
uv sync --locked
uv run manage.py migrate
uv run manage.py runserver
```

uv uses the Python 3.14 version pinned in `.python-version`, downloads it if needed, and creates `.venv` with the dependencies recorded in `uv.lock`. Open <http://127.0.0.1:8000/polls/> to view the application.

## Polls API

Django REST Framework provides a read-only API at <http://127.0.0.1:8000/api/polls/>.
Use `/api/polls/<id>/` to retrieve a single poll. Both endpoints return published
questions with their choices and vote counts; future questions are excluded.
Request `application/json` for JSON, or open either endpoint in a browser to use
the browsable API.

## JavaScript component showcase

Open <http://127.0.0.1:8000/polls/components/> or follow the showcase link on the
polls homepage. Alpine.js powers searchable poll cards and a native details
dialog; Chart.js displays vote counts as a bar or doughnut chart. The page reads
published polls from the existing API and links to the normal Django voting form.
Create questions and choices in the admin if the database has no published polls.
Use **Refresh results** to fetch updated vote counts.

Alpine.js 3.17.4 and Chart.js 4.5.1 are vendored with their MIT licenses under
`polls/static/polls/vendor/`. No CDN, Node installation, or frontend build is
required. The showcase code lives in `polls/static/polls/components.js` and
`polls/static/polls/components.css`, with markup in
`polls/templates/polls/components.html`.

## Development

Django Debug Toolbar appears on HTML pages when browsing from localhost with `DEBUG = True`. It is included in the application dependencies and disabled during tests. Click its handle on the right side of the page to inspect SQL queries, templates, and request details.

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
Regenerate the PaaS requirements file after changing application dependencies:

```sh
uv export --locked --no-dev --no-hashes --no-emit-project --output-file requirements.txt
```

## Production deployment

The [deployment guide](docs/deployment.md) covers native Python deployment on a PaaS,
managed PostgreSQL, required environment variables, migrations, and health checks.
Production defaults disable debug mode and require a strong secret key, explicit
allowed hosts, and PostgreSQL. Gunicorn serves the application, while WhiteNoise
serves compressed static files with content hashes for caching.
The PaaS dependency install includes Django Debug Toolbar and `psycopg[binary]`.

## Want Help Learning Django?
Check out [LearnDjango](https://learndjango.com) for dozens of free tutorials and premium courses to help you master web development with Python and Django.
