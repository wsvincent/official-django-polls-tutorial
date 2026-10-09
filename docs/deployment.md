# Deploying to a PaaS

Use your platform's native Python runtime with Python 3.14. The app runs with
Gunicorn, uses managed PostgreSQL through `psycopg[binary]`, and serves collected
static files through WhiteNoise. Gunicorn listens on the platform's `PORT`
(8000 by default). Django Debug Toolbar is included in the application dependency
install and activates when `DJANGO_DEBUG=true` for requests from `INTERNAL_IPS`.

## Environment variables

Set these in your PaaS dashboard before deploying:

| Variable | Production value |
| --- | --- |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_SECRET_KEY` | A newly generated random key of at least 50 characters |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames, such as `polls.example.com,my-app.onrender.com`; no schemes, paths, or `*` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins, such as `https://polls.example.com,https://my-app.onrender.com` |
| `DATABASE_URL` | The connection URL from your managed PostgreSQL service |

Generate a secret locally with `openssl rand -base64 64` and save it in the
platform's secret settings. Keep the same key across releases. Never use the
development key from `.env.example` in production.

Use the PostgreSQL provider's TLS connection settings. For a connection that
requires TLS, its URL should include `?sslmode=require` (or the provider's
certificate-verifying option). For example:
`postgresql://user:password@host:5432/polls?sslmode=require`.
The provider's private network may have different TLS requirements; preserve
the URL and options supplied by that provider.

Optional variables are `WEB_CONCURRENCY` (default 2 workers), `GUNICORN_THREADS`
(default 2 threads per worker), `DJANGO_DB_CONN_MAX_AGE` (default 60 seconds),
and `DJANGO_LOG_LEVEL` (default `INFO`). Size the worker count and PostgreSQL
connection limit for your platform's memory and instance count.

Production uses Django's SMTP email backend. The current polling flows do not
send email. Before enabling any email features, set `DJANGO_EMAIL_HOST`,
`DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`, and
`DJANGO_DEFAULT_FROM_EMAIL` to your email provider's values. SMTP defaults to
port 587 with STARTTLS; for port 465, set `DJANGO_EMAIL_PORT=465`,
`DJANGO_EMAIL_USE_TLS=false`, and `DJANGO_EMAIL_USE_SSL=true`.
Email delivery is not configured or verified by deployment alone.

The app assumes the PaaS terminates HTTPS, strips incoming `X-Forwarded-Proto`,
and sets that header itself. HTTPS redirection, secure cookies, and one-year
HSTS with subdomains and preload are enabled in production. Add every custom
domain to both host and CSRF settings before routing traffic to it.

## Native Python deployment

1. Push the prepared repository to your Git provider.
2. Create a managed PostgreSQL database and a web service from this repository.
3. Select the native Python runtime or builder and Python 3.14. Set the repository
   root as the working directory.
4. Set the environment variables above and the build/start commands below.
5. Set the pre-deploy/release command to `sh scripts/release.sh`. It applies
   migrations once before the new release serves traffic. If the plan does not
   support a pre-deploy command, run the migration command as a one-off job
   before activating the release.
6. Set the health-check path to `/healthz/`. It reports process liveness and
   supports HTTP probes without an HTTPS redirect; it does not test the database.
7. Deploy, then create an admin account with a one-off command:
   `.venv/bin/python manage.py createsuperuser` for a uv install, or
   `python manage.py createsuperuser` for a platform-managed Python environment.

Open `/polls/` or `/polls/components/` to use the application. The root URL
redirects to `/polls/`. The admin is at `/admin/`.

For a provider with uv available, use:

| Deployment phase | Command |
| --- | --- |
| Build | `sh scripts/build.sh` |
| Pre-deploy/release | `sh scripts/release.sh` |
| Start | `sh scripts/start.sh` |

Set production environment variables for release and runtime. The build installs
locked application dependencies and collects static files. `collectstatic` can
run without a secret key, allowed hosts, or database URL when the platform keeps
those variables out of the build environment. Its placeholder settings apply
only to that command; server startup and migrations still require the production
values. The release script runs Django's deployment checks before applying
migrations. The start command runs Gunicorn.

For a platform that installs packages with pip, use the committed
`requirements.txt` and this build command:

```sh
pip install -r requirements.txt && \
    python manage.py collectstatic --noinput
```

If the platform installs dependencies automatically from `uv.lock` or
`requirements.txt`, the build command is just `python manage.py collectstatic
--noinput`.

Use `sh scripts/start.sh` and `sh scripts/release.sh` for start and release;
they use `.venv` when it exists, otherwise the platform's Python environment.
Configure these commands in your platform's dashboard, with migrations as the
pre-deploy/release command.

WhiteNoise serves the collected Alpine.js, Chart.js, CSS, and admin assets.
Neither Node nor a separate static-file service is required. Django Debug Toolbar
is installed even when the build excludes the development dependency group;
production defaults still use `DJANGO_DEBUG=false`.

`requirements.txt` is generated from `uv.lock`. After changing dependencies,
regenerate it with:

```sh
uv export --locked --no-dev --no-hashes --no-emit-project --output-file requirements.txt
```

## Validation and operations

Run `uv run manage.py test` locally after copying `.env.example` to `.env`.
For deployment checks, run `python manage.py check --deploy --fail-level WARNING`
inside the PaaS shell or one-off environment with the real production
variables configured. `python manage.py migrate --check` confirms that migrations
have been applied. A healthy process alone does not confirm database connectivity;
check `/api/polls/` after release as well.

Enable managed PostgreSQL backups before accepting real votes. Local SQLite data
is not copied to PostgreSQL by deployment; transfer existing questions and choices
with Django's `dumpdata polls` and `loaddata` commands if you want to preserve them.
The app writes logs to the platform's log stream. The current application has no
uploaded media; future uploads need persistent object storage rather than the
service's temporary filesystem.
