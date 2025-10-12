from django.urls import path

from starminder.core.views import (
    DashboardView,
    DeleteAccountView,
    FAQView,
    HomepageView,
    TestimonialsView,
)

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("testimonials/", TestimonialsView.as_view(), name="testimonials"),
]
