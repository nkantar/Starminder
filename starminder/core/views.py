from typing import Any
import logging


from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseServerError
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import SettingsForm


logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"


class SettingsView(LoginRequiredMixin, FormView):
    form_class = SettingsForm
    template_name = "settings.html"
    success_url = reverse_lazy("dashboard")

    def get_initial(self) -> dict[Any, Any]:
        super_data = super().get_initial()

        profile = self.request.user.user_profile  # type: ignore[union-attr]

        profile_data = {
            "day": profile.day,
            "hour": profile.hour,
            "maximum": profile.maximum,
        }

        return {**super_data, **profile_data}

    def form_valid(self, form):
        form.instance.id = self.request.user.user_profile.id

        logger.info(form.is_valid())

        return super().form_valid(form)
