from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django_q.tasks import schedule


class Command(BaseCommand):
    help = "Generate content for a specific user"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "user_id",
            type=int,
            help="The ID of the user to generate content for",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        user_id = options["user_id"]
        schedule("starminder.implementations.jobs.generate_content", user_id)
