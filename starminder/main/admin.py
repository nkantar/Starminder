from django.contrib import admin
from django.contrib.admin import ModelAdmin

from starminder.main.models import Profile


class ProfileAdmin(ModelAdmin):
    list_display = ("id", "username", "email", "day", "time", "number")
    list_display_links = ("id", "username", "email")

admin.site.register(Profile, ProfileAdmin)
