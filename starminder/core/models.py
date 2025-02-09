from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
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
    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    def __str__(self) -> str:
        return self.email


class UserProfile(TimeStampedModel):
    user = OneToOneField(
        "core.CustomUser",
        on_delete=CASCADE,
        related_name="user_profile",
    )

    class Day(TextChoices):
        MONDAY = "Monday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"
        THURSDAY = "Thursday"
        FRIDAY = "Friday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        DAY = "day"

    class Hour(IntegerChoices):
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

    day = CharField(max_length=9, choices=Day, default=Day.DAY)
    hour = IntegerField(choices=Hour, default=Hour.ZERO)

    maximum = PositiveIntegerField(default=5)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile for {self.user.email}"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(
    sender: CustomUser,
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    UserProfile.objects.get_or_create(user=instance)
