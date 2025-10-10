from django.urls import path

from starminder.core.views import DashboardView, HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
