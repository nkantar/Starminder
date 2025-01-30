"""Core Starminder models."""

from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, DateTimeField, Model, OneToOneField
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


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(
    sender: CustomUser,  # noqa: ARG001
    instance: CustomUser,
    created: bool,  # noqa: ARG001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Create profile for newly created user."""
    UserProfile.objects.get_or_create(user=instance)
