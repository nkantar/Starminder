from typing import Any

from django.conf import settings
from django.db import migrations


DEFAULT_SITE_DOMAIN_NAME = "example.com"
DEFAULT_SITE_DISPLAY_NAME = "example.com"


def update_default_site(
    apps: Any, site_domain_name: str, site_display_name: str
) -> None:
    Site = apps.get_model("sites", "Site")
    site = Site.objects.get_or_create(pk=settings.SITE_ID)[0]
    site.domain = site_domain_name
    site.name = site_display_name
    site.save()


def update_default_site_forward(apps: Any, schema_editor: Any) -> None:
    update_default_site(
        apps=apps,
        site_domain_name=settings.DJANGO_SITE_DOMAIN_NAME,
        site_display_name=settings.DJANGO_SITE_DISPLAY_NAME,
    )


def reverse_update_default_site(apps: Any, schema_editor: Any) -> None:
    update_default_site(
        apps=apps,
        site_domain_name=DEFAULT_SITE_DOMAIN_NAME,
        site_display_name=DEFAULT_SITE_DISPLAY_NAME,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            update_default_site_forward,
            reverse_code=reverse_update_default_site,
        )
    ]
