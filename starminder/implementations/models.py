from django.conf import settings
from django.db.models import CASCADE, ForeignKey, Manager

from starminder.core.models import StarFieldsBase, TimestampedModel


class TempStar(TimestampedModel, StarFieldsBase):
    objects: "Manager[TempStar]"

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    class Meta:
        verbose_name = "Temporary Star"

    def __str__(self) -> str:
        return f"tmp: {self.owner}/{self.name}, {self.provider}, {self.user.username}"
