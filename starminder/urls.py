from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView


urlpatterns = [
    path("", include("starminder.core.urls")),
    path("reminders/", include("starminder.content.urls")),
    path(f"{settings.ADMIN_PREFIX}admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # 301 redirects from old /content/ paths to new /reminders/ paths
    re_path(
        r"^content/(?P<path>.*)$",
        RedirectView.as_view(url="/reminders/%(path)s", permanent=True),
    ),
]
