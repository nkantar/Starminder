from django import forms

from starminder.core.models import UserProfile


class UserProfileConfigForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["reminder_email", "max_entries", "day_of_week", "hour_of_day"]
        widgets = {
            "reminder_email": forms.EmailInput(),
            "max_entries": forms.NumberInput(attrs={"min": 1, "max": 100}),
            "day_of_week": forms.Select(),
            "hour_of_day": forms.NumberInput(attrs={"min": 0, "max": 23}),
        }
        labels = {
            "reminder_email": "Reminder email address",
            "max_entries": "Maximum entries per reminder",
            "day_of_week": "Day of week",
            "hour_of_day": "Hour of day (0-23)",
        }
