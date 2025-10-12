from django.conf import settings

from starminder.core.models import CustomUser


def global_settings(request):
    user_count = CustomUser.objects.filter(is_staff=False).count()
    return {
        "VERSION": settings.STARMINDER_VERSION,
        "USER_COUNT": user_count,
    }
