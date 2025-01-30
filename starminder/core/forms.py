"""Core Starminder forms."""

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):  # type: ignore[type-arg]
    """Override of built-in user creation form."""

    class Meta:
        """Meta settings for form."""

        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):  # type: ignore[type-arg]
    """Override of built-in user change form."""

    class Meta:
        """Meta settings for form."""

        model = CustomUser
        fields = ("username", "email")
