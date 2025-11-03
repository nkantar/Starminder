from django import forms

from starminder.core.models import UserProfile


def _coerce(value: str) -> bool:
    return value == "True"


class UserProfileConfigForm(forms.ModelForm):
    INCLUDE_CHOICES = [
        (True, "Include"),
        (False, "Don't include"),
    ]

    include_archived = forms.TypedChoiceField(
        choices=INCLUDE_CHOICES,
        coerce=_coerce,
        widget=forms.Select(),
    )
    include_own = forms.TypedChoiceField(
        choices=INCLUDE_CHOICES,
        coerce=_coerce,
        widget=forms.Select(),
    )

    class Meta:
        model = UserProfile
        fields = [
            "reminder_email",
            "max_entries",
            "day_of_week",
            "hour_of_day",
            "include_archived",
            "include_own",
        ]
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
            "include_archived": "Archived repositories",
            "include_own": "Own repositories",
        }
