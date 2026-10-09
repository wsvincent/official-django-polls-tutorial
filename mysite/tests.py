import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class ProductionSettingsTests(SimpleTestCase):
    def load_settings(self, argv=None, **overrides) -> dict[str, Any]:
        environment = {
            "DJANGO_SECRET_KEY": "production-test-key-with-at-least-fifty-characters-1234567890",
            "DJANGO_ALLOWED_HOSTS": "polls.example.com",
            "DATABASE_URL": "postgresql://test:test@localhost/polls?sslmode=require",
            **overrides,
        }
        environment = {
            name: value for name, value in environment.items() if value is not None
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(sys, "argv", argv if argv is not None else ["gunicorn"]),
            patch("environ.Env.read_env"),
        ):
            settings_path = Path(__file__).with_name("settings.py")
            configuration: dict[str, Any] = {"__file__": str(settings_path)}
            # Preserve the management command's argv, which runpy replaces.
            exec(
                compile(settings_path.read_text(), str(settings_path), "exec"),
                configuration,
            )
            return configuration

    def test_collectstatic_works_without_runtime_environment_variables(self):
        configuration = self.load_settings(
            argv=["manage.py", "collectstatic", "--noinput"],
            DJANGO_SECRET_KEY=None,
            DJANGO_ALLOWED_HOSTS=None,
            DATABASE_URL=None,
        )

        self.assertFalse(configuration["DEBUG"])
        self.assertFalse(configuration["TESTING"])
        self.assertTrue(configuration["COLLECTING_STATIC"])
        self.assertEqual(configuration["DATABASES"]["default"]["NAME"], ":memory:")
        self.assertEqual(
            configuration["STORAGES"]["staticfiles"]["BACKEND"],
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )

    def test_static_defaults_do_not_apply_to_runtime_or_release_commands(self):
        commands = (
            ["gunicorn", "mysite.wsgi:application"],
            ["gunicorn", "collectstatic"],
            ["gunicorn", "mysite.wsgi:application", "--name", "collectstatic"],
            ["manage.py", "check", "--deploy"],
            ["manage.py", "migrate", "--noinput"],
        )
        for argv in commands:
            with (
                self.subTest(argv=argv),
                self.assertRaisesMessage(ImproperlyConfigured, "DJANGO_SECRET_KEY"),
            ):
                self.load_settings(argv=argv, DJANGO_SECRET_KEY=None)

    def test_production_defaults_require_https_and_postgresql(self):
        configuration = self.load_settings()

        self.assertFalse(configuration["DEBUG"])
        self.assertTrue(configuration["SECURE_SSL_REDIRECT"])
        self.assertTrue(configuration["SESSION_COOKIE_SECURE"])
        self.assertTrue(configuration["CSRF_COOKIE_SECURE"])
        self.assertGreater(configuration["SECURE_HSTS_SECONDS"], 0)
        self.assertEqual(configuration["ALLOWED_HOSTS"], ["polls.example.com"])
        self.assertEqual(
            configuration["DATABASES"]["default"]["ENGINE"],
            "django.db.backends.postgresql",
        )
        self.assertEqual(
            configuration["DATABASES"]["default"]["OPTIONS"]["sslmode"], "require"
        )
        self.assertNotIn("debug_toolbar", configuration["INSTALLED_APPS"])
        self.assertEqual(
            configuration["STORAGES"]["staticfiles"]["BACKEND"],
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
        )
        self.assertEqual(
            configuration["MAILERS"]["default"]["BACKEND"],
            "django.core.mail.backends.smtp.EmailBackend",
        )

    def test_production_smtp_options_use_the_environment(self):
        configuration = self.load_settings(
            DJANGO_EMAIL_HOST="smtp.example.com",
            DJANGO_EMAIL_PORT="465",
            DJANGO_EMAIL_HOST_USER="test-user",
            DJANGO_EMAIL_HOST_PASSWORD="test-password",
            DJANGO_EMAIL_USE_TLS="false",
            DJANGO_EMAIL_USE_SSL="true",
        )
        options = configuration["MAILERS"]["default"]["OPTIONS"]

        self.assertEqual(options["host"], "smtp.example.com")
        self.assertEqual(options["port"], 465)
        self.assertEqual(options["username"], "test-user")
        self.assertEqual(options["password"], "test-password")
        self.assertFalse(options["use_tls"])
        self.assertTrue(options["use_ssl"])

    def test_production_rejects_an_insecure_secret(self):
        for secret in ("", "short-key", "django-insecure-" + "x" * 60):
            with self.subTest(secret=secret), self.assertRaises(ImproperlyConfigured):
                self.load_settings(DJANGO_SECRET_KEY=secret)

    def test_production_requires_a_secret_key(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DJANGO_SECRET_KEY"):
            self.load_settings(DJANGO_SECRET_KEY=None)

    def test_production_requires_explicit_hosts(self):
        for hosts in ("", "*", "polls.example.com,*"):
            with self.subTest(hosts=hosts), self.assertRaises(ImproperlyConfigured):
                self.load_settings(DJANGO_ALLOWED_HOSTS=hosts)

    def test_production_rejects_sqlite(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "must use PostgreSQL"):
            self.load_settings(DATABASE_URL="sqlite:///db.sqlite3")

    def test_production_requires_database_url(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "DATABASE_URL"):
            self.load_settings(DATABASE_URL=None)


@override_settings(
    SECURE_SSL_REDIRECT=True,
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
)
class PlatformRoutingTests(SimpleTestCase):
    def test_http_health_probe_succeeds_without_a_database(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_health_probe_supports_head(self):
        response = self.client.head(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_public_http_requests_redirect_to_https(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://testserver/")

    def test_https_proxy_header_avoids_a_redirect_loop(self):
        response = self.client.get(reverse("home"), HTTP_X_FORWARDED_PROTO="https")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("polls:index"))
