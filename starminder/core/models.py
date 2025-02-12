from typing import Any
import logging

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    DateTimeField,
    Model,
    OneToOneField,
    PositiveIntegerField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver


logger = logging.getLogger(__name__)


class TimeStampedModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    user_profile: "UserProfile"

    def __str__(self) -> str:
        return self.email


class UserProfile(TimeStampedModel):
    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name="user_profile")

    day = PositiveIntegerField(default=0)
    hour = PositiveIntegerField(default=0)

    maximum = PositiveIntegerField(default=5)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile for {self.user}"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(
    sender: CustomUser,
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    UserProfile.objects.get_or_create(user=instance)
