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


class Post(TimestampedModel):
    objects: "Manager[Post]"

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)


class Entry(TimestampedModel):
    objects: "Manager[Entry]"

    post = ForeignKey(Post, on_delete=CASCADE)
    provider = CharField(max_length=255)
    provider_id = CharField(max_length=255)
    owner = CharField(max_length=255)
    owner_id = CharField(max_length=255)
    description = CharField(max_length=500, null=True, blank=True)
    star_count = IntegerField()
    repo_url = URLField()
    project_url = URLField(null=True, blank=True)

    class Meta:
        verbose_name = "Entrie"
        verbose_name_plural = "Entries"
