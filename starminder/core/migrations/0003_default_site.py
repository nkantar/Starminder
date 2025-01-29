from django.conf import settings
from django.db import migrations


DEFAULT_SITE_DOMAIN_NAME = "example.com"
DEFAULT_SITE_DISPLAY_NAME = "example.com"


def update_default_site(apps, site_domain_name, site_display_name):
    Site = apps.get_model("sites", "Site")
    site = Site.objects.get(pk=settings.SITE_ID)
    site.domain = site_domain_name
    site.name = site_display_name
    site.save()


def update_default_site_forward(apps, schema_editor):
    update_default_site(
        apps=apps,
        site_domain_name=settings.SITE_DOMAIN_NAME,
        site_display_name=settings.SITE_DISPLAY_NAME,
    )


def reverse_update_default_site(apps, schema_editor):
    update_default_site(
        apps=apps,
        site_domain_name=DEFAULT_SITE_DOMAIN_NAME,
        site_display_name=DEFAULT_SITE_DISPLAY_NAME,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_userprofile"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(
            update_default_site_forward,
            reverse_code=reverse_update_default_site,
        )
    ]
