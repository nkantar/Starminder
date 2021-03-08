from django.conf import settings
from django.contrib import messages

from starminder.main.models import Profile


class StarminderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class EmailRequiredMiddleware(StarminderMiddleware):
    def process_template_response(self, request, response):
        if request.user.is_authenticated and not request.user.email:
            messages.add_message(request, messages.ERROR, "Email required!")
        return response


class FooterStatsMiddleware(StarminderMiddleware):
    def process_template_response(self, request, response):
        response.context_data["profile_count"] = Profile.objects.count()
        response.context_data["starminder_version"] = settings.STARMINDER_VERSION
        return response
