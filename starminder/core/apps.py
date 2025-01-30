"""Core Starminder app."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core Starminder app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "starminder.core"
