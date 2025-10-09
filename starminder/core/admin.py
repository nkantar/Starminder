from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from starminder.core.models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)
