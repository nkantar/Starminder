from datetime import time

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView

from starminder.main.forms import ProfileForm


class HomeView(TemplateView):
    template_name = "home.html"


@method_decorator(login_required(login_url="/"), name="dispatch")
class DashboardView(FormView):
    form_class = ProfileForm
    template_name = "dashboard.html"
    success_url = reverse_lazy("dashboard")

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "number": self.request.user.profile.number,
                "day": self.request.user.profile.day,
                "time": self.request.user.profile.time,
                "email": self.request.user.email,
            }
        )

        return initial

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = self.request.user
            user.email = form.data["email"]
            user.save()

            profile = user.profile
            profile.number = int(form.data["number"])
            profile.day = int(form.data["day"])
            profile.time = time.fromisoformat(form.data["time"])
            profile.save()

            return self.form_valid(form)

        else:
            return self.form_invalid(form)
