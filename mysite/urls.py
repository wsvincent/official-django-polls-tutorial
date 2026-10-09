from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from .health import health

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="polls:index"), name="home"),
    path("healthz/", health, name="health"),
    path("polls/", include("polls.urls")),
    path("api/", include("polls.api_urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG and not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
