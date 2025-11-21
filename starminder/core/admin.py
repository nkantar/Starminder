from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from starminder.core.models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "profile_link",
    ]
    list_display_links = ["id", "username"]

    @admin.display(description="Profile")
    def profile_link(self, obj: CustomUser) -> str:
        if hasattr(obj, "user_profile") and isinstance(obj.user_profile, UserProfile):
            url = reverse("admin:core_userprofile_change", args=[obj.user_profile.id])
            return format_html('<a href="{}">{}</a>', url, obj.user_profile)
        return "-"


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user_link",
        "feed_id",
        "reminder_email",
        "max_entries",
        "day_of_week",
        "hour_of_day",
        "enabled",
    ]
    list_filter = ["enabled"]

    @admin.display(description="User", ordering="user__username")
    def user_link(self, obj: UserProfile) -> str:
        url = reverse("admin:core_customuser_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
