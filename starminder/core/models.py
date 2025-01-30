"""Core Starminder models."""

from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerChoices,
    IntegerField,
    Model,
    OneToOneField,
    PositiveIntegerField,
    TextChoices,
)
from django.db.models.signals import post_save
from django.dispatch import receiver


class TimeStampedModel(Model):
    """Base class to timestamp everything."""

    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

    class Meta:
        """Meta settings for model."""

        abstract = True


class CustomUser(AbstractUser):
    """Override of built-in User class."""

    def __str__(self) -> str:
        """Represent instance as string."""
        return self.email


class UserProfile(TimeStampedModel):
    """Profile for extra user data."""

    user = OneToOneField("core.CustomUser", on_delete=CASCADE)

    class Meta:
        """Meta settings for model."""

        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        """Represent instance as string."""
        return f"Profile for {self.user.email}"


class Configuration(TimeStampedModel):
    """Provider configuration."""

    class Day(TextChoices):
        """Day of week."""

        MONDAY = "Monday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"
        THURSDAY = "Thursday"
        FRIDAY = "Friday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        DAY = "day"

    class Hour(IntegerChoices):
        """Hour of day."""

        ZERO = 0
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6
        SEVEN = 7
        EIGHT = 8
        NINE = 9
        TEN = 10
        ELEVEN = 11
        TWELVE = 12
        THIRTEEN = 13
        FOURTEEN = 14
        FIFTEEN = 15
        SIXTEEN = 16
        SEVENTEEN = 17
        EIGHTEEN = 18
        NINETEEN = 19
        TWENTY = 20
        TWENTYONE = 21
        TWENTYTWO = 22
        TWENTYTHREE = 23

    profile = ForeignKey(UserProfile, on_delete=CASCADE)

    day = CharField(max_length=9, choices=Day, default=Day.DAY)
    hour = IntegerField(choices=Hour, default=Hour.ZERO)

    maximum = PositiveIntegerField(default=5)

    active = BooleanField(default=True)

    def __str__(self) -> str:
        """Represent instance as string."""
        return f"Configuration for {self.profile}"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(
    sender: CustomUser,  # noqa: ARG001
    instance: CustomUser,
    created: bool,  # noqa: ARG001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Create profile for newly created user."""
    UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserProfile)
def create_default_settings(
    sender: UserProfile,  # noqa: ARG001
    instance: UserProfile,
    created: bool,
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Create default settings for newly created user profile."""
    if created:
        Configuration.objects.create(profile=instance)
