from typing import Any
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    DateTimeField,
    Manager,
    Model,
    OneToOneField,
    UUIDField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver


class TimestampedModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    user_profile = "CustomUser"

    def __str__(self):
        return f"{self.username} (User)"

    class Meta:
        verbose_name = "Custom User"


class UserProfile(TimestampedModel):
    objects: "Manager[UserProfile]"

    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name="user_profile")
    feed_id = UUIDField(default=uuid4, unique=True)

    def __str__(self):
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
