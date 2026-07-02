from http import HTTPMethod
from typing import Any, cast

from allauth.socialaccount.models import SocialAccount, SocialToken
import httpx
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from starminder.core.forms import UserProfileConfigForm
from starminder.core.models import CustomUser


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
        kwargs["instance"] = cast(CustomUser, self.request.user).user_profile
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["socialaccount_list"] = SocialAccount.objects.filter(
            user=self.request.user
        )
        context["user_profile"] = cast(CustomUser, self.request.user).user_profile
        context["page_title"] = "Dashboard"
        return context

    def form_valid(self, form: UserProfileConfigForm) -> HttpResponse:
        form.save()
        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        user = cast(CustomUser, request.user)
        for social_account in user.socialaccount_set.all():
            for social_token in SocialToken.objects.filter(account=social_account):
                app_client_id = social_token.app.client_id

                httpx.request(
                    method=HTTPMethod.DELETE,
                    url=f"https://api.github.com/applications/{app_client_id}/grant",
                    auth=(social_token.app.client_id, social_token.app.secret),
                    headers={
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Vesrion": "2022-11-28",
                    },
                    json={"access_token": social_token.token},
                )

        user.delete()
        logout(request)
        return redirect("homepage")
