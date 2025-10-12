from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from allauth.socialaccount.models import SocialAccount

from starminder.core.forms import UserProfileConfigForm


class HomepageView(TemplateView):
    template_name = "home.html"
    extra_context = {"page_title": "This is Starminder."}


class FAQView(TemplateView):
    template_name = "faq.html"
    extra_context = {"page_title": "FAQ"}


class TestimonialsView(TemplateView):
    template_name = "testimonials.html"
    extra_context = {"page_title": "Testimonials"}


class DashboardView(LoginRequiredMixin, FormView):
    template_name = "dash.html"
    form_class = UserProfileConfigForm
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user.user_profile
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["socialaccount_list"] = SocialAccount.objects.filter(
            user=self.request.user
        )
        context["user_profile"] = self.request.user.user_profile
        context["page_title"] = "Dashboard"
        return context

    def form_valid(self, form: UserProfileConfigForm) -> HttpResponse:
        form.save()
        return super().form_valid(form)
