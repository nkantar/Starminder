from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    EmailField,
    IntegerField,
    Manager,
    Model,
    OneToOneField,
    PositiveIntegerField,
    Q,
    QuerySet,
    TextField,
    URLField,
    UUIDField,
)
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_q.tasks import schedule

from starminder.core.push import send_push_notification


class TimestampedModel(Model):
    id: int
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StarFieldsBase(Model):
    """Abstract base model containing shared fields for star-related models."""

    provider = CharField(max_length=255)
    provider_id = CharField(max_length=255)
    name = CharField(max_length=255)
    owner = CharField(max_length=255)
    owner_id = CharField(max_length=255)
    description = TextField(null=True, blank=True)
    star_count = IntegerField()
    repo_url = URLField(max_length=1024)
    project_url = URLField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    id: int
    user_profile = "CustomUser"

    def __str__(self) -> str:
        return f"{self.username} (User)"

    class Meta:
        verbose_name = "Custom User"


class UserProfileManager(Manager["UserProfile"]):
    def scheduled_for(self, now: datetime) -> "QuerySet[UserProfile]":
        current_day = now.weekday()
        current_hour = now.hour

        return self.get_queryset().filter(
            Q(day_of_week=current_day) | Q(day_of_week=UserProfile.EVERY_DAY),
            hour_of_day=current_hour,
        )


class UserProfile(TimestampedModel):
    EVERY_DAY = -1
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    DAY_OF_WEEK_CHOICES = [
        (EVERY_DAY, "day"),
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]

    objects: UserProfileManager = UserProfileManager()

    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name="user_profile")
    feed_id = UUIDField(default=uuid4, unique=True)
    reminder_email = EmailField(null=True, blank=True)

    max_entries = PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    day_of_week = IntegerField(choices=DAY_OF_WEEK_CHOICES, default=EVERY_DAY)
    hour_of_day = IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
    )

    def __str__(self) -> str:
        return f"{self.user.username} (Profile)"

    class Meta:
        verbose_name = "User Profile"


@receiver(post_save, sender=CustomUser)
def create_user_profile(
    sender: type[CustomUser],
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={"reminder_email": instance.email},
        )
        schedule(
            "starminder.implementations.jobs.user_job",
            instance.id,
            next_run=datetime.now() + timedelta(minutes=1),
        )
        if not settings.DEBUG:
            send_push_notification(
                message=f"New user signed up: {instance.username}",
                title="New Starminder Signup",
            )


@receiver(post_delete, sender=UserProfile)
def notify_user_profile_deletion(
    sender: type[UserProfile],
    instance: UserProfile,
    **kwargs: Any,
) -> None:
    if not settings.DEBUG:
        send_push_notification(
            message=f"User deleted their account: {instance.user.username}",
            title="Starminder Account Deletion",
        )
