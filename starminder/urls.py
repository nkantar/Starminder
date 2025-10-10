from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("starminder.core.urls")),
    path("feeds/", include("starminder.content.urls")),
    path(f"{settings.ADMIN_PREFIX}admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]
