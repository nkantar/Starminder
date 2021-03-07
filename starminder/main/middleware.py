from django.conf import settings

from starminder.main.models import Profile


class FooterStatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        response.context_data["profile_count"] = Profile.objects.count()
        response.context_data["starminder_version"] = settings.STARMINDER_VERSION
        return response
