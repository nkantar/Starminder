from django.core.management.base import BaseCommand

from starminder.implementations.jobs import start_jobs


class Command(BaseCommand):
    help = "Schedule content generation jobs for all applicable users"

    def handle(self, *args, **options):
        start_jobs()
