# from django.views.generic import FormView, TemplateView
from django.views.generic import TemplateView

# from .forms import ConfigurationForm
# from .models import Configuration


class HomeView(TemplateView):
    template_name = "home.html"


class DashboardView(TemplateView):
    template_name = "dashboard.html"


# class SettingsView(FormView):
#     form_class = ConfigurationForm
#     template_name = "settings.html"

#     def get_form_kwargs(self) -> dict[Any, Any]:
#         super_kwargs = super().get_form_kwargs()
#         configuration = self.request.user.user_profile.configuration.first()
#         return {
#             **super_kwargs,
#             "initial": {
#                 **super_kwargs["initial"],
#                 "day": configuration.day,
#                 "hour": configuration.hour,
#                 "maximum": configuration.maximum,
#                 "active": configuration.active,
#             },
#         }
