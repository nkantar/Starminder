from typing import Any

from django.conf import settings
from django.http import HttpRequest

from starminder.core.models import CustomUser


def global_settings(request: HttpRequest) -> dict[str, Any]:
    user_count = CustomUser.objects.filter(is_staff=False).count()
    return {
        "VERSION": settings.STARMINDER_VERSION,
        "USER_COUNT": user_count,
    }
