from datetime import time as d_time

from django.forms import (
    ChoiceField,
    EmailField,
    Form,
    IntegerField,
)


DAYS = [
    (0, "every day"),
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]

TIMES = [(d_time(hour), f"{hour}:00") for hour in range(0, 24)]


class ProfileForm(Form):
    number = IntegerField(label="How many stars", min_value=1)
    day = ChoiceField(label="Day of week", choices=DAYS)
    time = ChoiceField(label="Time of day (UTC)", choices=TIMES)
    email = EmailField(label="Email address", required=True)
