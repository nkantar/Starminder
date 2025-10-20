from django.conf import settings
from django.db.models import CASCADE, ForeignKey, Manager
import emoji

from starminder.core.models import StarFieldsBase, TimestampedModel


TIMESTAMP_FORMAT = "%A %Y-%m-%d %H:%M:%S"


class Reminder(TimestampedModel):
    objects: "Manager[Reminder]"
    star_set: "Manager[Star]"

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    class Meta:
        verbose_name = "Reminder"

    def __str__(self) -> str:
        return f"{self.user.username}, {self.created_at.date()}"

    @property
    def title(self) -> str:
        return f"Reminder: {self.created_at.strftime(TIMESTAMP_FORMAT)}"


class Star(TimestampedModel, StarFieldsBase):
    objects: "Manager[Star]"

    reminder = ForeignKey(Reminder, on_delete=CASCADE)

    class Meta:
        verbose_name = "Star"

    def __str__(self) -> str:
        return f"{self.owner}/{self.name}, {self.provider}, {self.reminder}"

    @property
    def description_pretty(self) -> str:
        return emoji.emojize(self.description, language="alias")
