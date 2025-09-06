from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm, Select

from .models import CustomUser, UserProfile


DAY_OPTIONS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
    "day",
]


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class SettingsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["day", "hour", "maximum"]
        widgets = {
            "day": Select(
                choices=tuple([(idx, day) for idx, day in enumerate(DAY_OPTIONS)]),
            ),
            "hour": Select(choices=tuple([(hour, f"{hour}:00") for hour in range(24)])),
        }
