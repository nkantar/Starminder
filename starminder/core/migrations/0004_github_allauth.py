from django.conf import settings
from django.db import migrations


PROVIDER_NAME = "github"


def create_github_social_app(apps, schema_editor):
    SocialApp = apps.get_model("socialaccount", "SocialApp")
    app = SocialApp(
        provider=PROVIDER_NAME,
        name=settings.APP_NAME,
        client_id=settings.GITHUB_CLIENT_ID,
        secret=settings.GITHUB_CLIENT_SECRET,
    )
    app.save()
    app.sites.set([settings.SITE_ID])
    app.save()


def delete_github_social_app(apps, schema_editor):
    # SocialApp = apps.get_model("socialaccount", "SocialApp")
    # app = SocialApp.objects.get(name=settings.APP_NAME)
    # app.delete()
    pass  # TODO why isn't this working?


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_default_site"),
    ]

    operations = [
        migrations.RunPython(
            create_github_social_app,
            reverse_code=delete_github_social_app,
        ),
    ]
