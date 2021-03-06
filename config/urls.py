from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(f"{settings.ADMIN_PREFIX}/admin/", admin.site.urls),
    path("", include("starminder.main.urls")),
]
