"""Core Starminder admin config."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):  # type: ignore[type-arg]
    """Inline UserProfile definition for inclusion in CustomUser."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"  # TODO is this wrong?


class CustomUserAdmin(UserAdmin):  # type: ignore[type-arg]
    """Admin config for CustomUser."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username"]
    inlines = [UserProfileInline]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)
