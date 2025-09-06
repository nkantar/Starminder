from typing import Any
import logging


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from neapolitan.views import CRUDView

from .forms import SettingsForm
from .models import UserProfile


logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"


class SettingsView(LoginRequiredMixin, CRUDView):
    def get_object(self) -> UserProfile:
        return UserProfile.objects.get(pk=self.request.user.user_profile.pk)

    def get_success_url(self) -> str:
        return reverse("settings")

    model = UserProfile
    fields = ["day", "hour", "maximum"]
    form_class = SettingsForm
