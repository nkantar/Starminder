from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomepageView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dash.html"
