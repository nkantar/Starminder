from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, DateTimeField, Manager, Model, OneToOneField
from django.db.models.signals import post_save
from django.dispatch import receiver


class TimestampedModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    user_profile = "CustomUser"


class UserProfile(TimestampedModel):
    objects: "Manager[UserProfile]"

    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name="user_profile")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=CustomUser)
def create_user_profile(
    sender: type[CustomUser],
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    if created:
        UserProfile.objects.get_or_create(user=instance)
