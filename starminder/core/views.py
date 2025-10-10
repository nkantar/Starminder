from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from allauth.socialaccount.models import SocialAccount


class HomepageView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dash.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["socialaccount_list"] = SocialAccount.objects.filter(
            user=self.request.user
        )
        return context
