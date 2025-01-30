"""Starminder core views."""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Show default homepage."""

    template_name = "home.html"


class DashboardView(TemplateView):
    """Show user dashboard."""

    template_name = "dashboard.html"
