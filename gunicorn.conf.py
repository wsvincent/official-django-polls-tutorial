import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = 30
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = os.environ.get("DJANGO_LOG_LEVEL", "info").lower()
