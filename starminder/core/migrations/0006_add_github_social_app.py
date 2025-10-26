
import os
from django.db import migrations

def add_github_social_app(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')

    site = Site.objects.get(pk=1)

    client_id = os.environ.get('GITHUB_CLIENT_ID')
    secret = os.environ.get('GITHUB_CLIENT_SECRET')

    if client_id and secret:
        social_app, created = SocialApp.objects.get_or_create(
            provider='github',
            defaults={
                'name': 'GitHub',
                'client_id': client_id,
                'secret': secret,
            }
        )
        if created:
            social_app.sites.add(site)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_userprofile_max_entries'),
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
    ]

    operations = [
        migrations.RunPython(add_github_social_app),
    ]
