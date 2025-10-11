from datetime import datetime
from typing import Any
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    DateTimeField,
    IntegerField,
    Manager,
    Model,
    OneToOneField,
    PositiveIntegerField,
    Q,
    QuerySet,
    UUIDField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver


class TimestampedModel(Model):
    id: int
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
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

    max_entries = PositiveIntegerField(default=5, validators=[MinValueValidator(1)])
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
        UserProfile.objects.get_or_create(user=instance)
