from django.conf import settings
from django.contrib.sites.models import Site
from django.db import migrations


def rename_default_site(apps, schema_editor):
    site = Site.objects.get(pk=1)
    site.domain = settings.DEFAULT_DOMAIN
    site.save()


class Migration(migrations.Migration):

    dependencies = [
        ("socialaccount", "0003_extra_data_default_dict"),
    ]

    operations = [
        migrations.RunPython(rename_default_site),
    ]
