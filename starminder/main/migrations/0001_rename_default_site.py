from django.conf import settings
from django.contrib.sites.models import Site
from django.db import migrations


def rename_default_site(apps, schema_editor):
    try:
        site = Site.objects.get(pk=1)
        site.domain = settings.DEFAULT_DOMAIN
        site.name = "Starminder"
        site.save()
    except Site.DoesNotExist:
        site = Site.objects.create(
            domain=settings.DEFAULT_DOMAIN,
            name="Starminder",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("socialaccount", "0003_extra_data_default_dict"),
    ]

    operations = [
        migrations.RunPython(rename_default_site),
    ]
