from typing import Any

from django.core.management.base import BaseCommand
from django_q.models import Schedule
from loguru import logger


class Command(BaseCommand):
    help = "Set up django-q schedules for recurring jobs"

    def handle(self, *args: Any, **options: Any) -> None:
        schedule, created = Schedule.objects.get_or_create(
            name="start_jobs_hourly",
            defaults={
                "func": "starminder.implementations.jobs.start_jobs",
                "schedule_type": Schedule.CRON,
                "cron": "5 * * * *",
            },
        )

        logger.info(
            f"Schedule {'created' if created else 'already exists'}: {schedule.name}"
        )
