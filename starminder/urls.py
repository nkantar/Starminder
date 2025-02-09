from django.conf import settings
from django.contrib import admin
from django.urls import include, path

# from starminder.core.views import DashboardView, HomeView, SettingsView
from starminder.core.views import DashboardView, HomeView

urlpatterns = [
    path(f"{settings.ADMIN_PREFIX}admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # path("settings/", SettingsView.as_view(), name="settings"),
    path("", HomeView.as_view(), name="home"),
]
