from django.core.management.base import BaseCommand

from starminder.main.email import send_emails


class Command(BaseCommand):
    help = "Send emails for the current hour"

    def handle(self, *args, **options):
        send_emails()
