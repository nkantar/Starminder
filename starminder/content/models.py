from django.conf import settings
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    IntegerField,
    Manager,
    URLField,
)

from starminder.core.models import TimestampedModel


class Reminder(TimestampedModel):
    objects: "Manager[Reminder]"
    entry_set: "Manager[Entry]"

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    class Meta:
        verbose_name = "Reminder"

    def __str__(self) -> str:
        return f"{self.user.username}, {self.created_at.date()}"


class Entry(TimestampedModel):
    objects: "Manager[Entry]"

    reminder = ForeignKey(Reminder, on_delete=CASCADE)

    provider = CharField(max_length=255)
    provider_id = CharField(max_length=255)
    name = CharField(max_length=255)
    owner = CharField(max_length=255)
    owner_id = CharField(max_length=255)
    description = CharField(max_length=500, null=True, blank=True)
    star_count = IntegerField()
    repo_url = URLField()
    project_url = URLField(null=True, blank=True)

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __str__(self) -> str:
        return f"{self.owner}/{self.name}, {self.provider}, {self.reminder}"
