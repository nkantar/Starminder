from datetime import datetime
from typing import Any

from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.views.generic import DetailView, ListView

from starminder.content.models import Reminder
from starminder.core.models import UserProfile


class ReminderListView(ListView):
    template_name = "reminder_list.html"
    context_object_name = "reminders"
    extra_context = {"page_title": "Reminders"}

    def get_queryset(self) -> QuerySet[Reminder]:
        feed_id = self.kwargs["feed_id"]
        user_profile = get_object_or_404(UserProfile, feed_id=feed_id)
        return (
            Reminder.objects.filter(user=user_profile.user)
            .prefetch_related("star_set")
            .order_by("-created_at")
        )


class ReminderDetailView(DetailView):
    template_name = "reminder.html"
    context_object_name = "reminder"
    pk_url_kwarg = "reminder_id"

    def get_queryset(self) -> QuerySet[Reminder]:
        feed_id = self.kwargs["feed_id"]
        user_profile = get_object_or_404(UserProfile, feed_id=feed_id)
        return Reminder.objects.filter(user=user_profile.user).prefetch_related(
            "star_set"
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return {**context, "page_title": self.object.title}


class AtomFeedView(Feed):
    feed_type = Atom1Feed

    def get_object(self, request: HttpRequest, feed_id: str) -> UserProfile:
        self.request = request
        return get_object_or_404(UserProfile, feed_id=feed_id)

    def title(self, obj: UserProfile) -> str:
        return f"Starminder Feed - {obj.user.username}"

    def link(self, obj: UserProfile) -> str:
        return self.request.build_absolute_uri(f"/content/{obj.feed_id}/")

    def description(self, obj: UserProfile) -> str:
        return f"Starred repository reminders for {obj.user.username}"

    def items(self, obj: UserProfile) -> QuerySet[Reminder]:
        return (
            Reminder.objects.filter(user=obj.user)
            .prefetch_related("user", "star_set")
            .order_by("-created_at")
        )

    def item_title(self, item: Reminder) -> str:
        return f"Reminder from {item.created_at.strftime('%Y-%m-%d %H:%M')}"

    def item_description(self, item: Reminder) -> str:
        stars = item.star_set.all()
        if not stars:
            return "No stars in this reminder."

        lines = []
        for star in stars:
            lines.append(f"<h3>{star.owner}/{star.name} ({star.provider})</h3>")
            if star.description:
                lines.append(f"<p>{star.description}</p>")
            lines.append(f"<p>Stars: {star.star_count}</p>")
            lines.append(f'<p><a href="{star.repo_url}">Repository</a>')
            if star.project_url:
                lines.append(f' | <a href="{star.project_url}">Project</a>')
            lines.append("</p>")

        return "\n".join(lines)

    def item_link(self, item: Reminder) -> str:
        return f"/content/{item.user.user_profile.feed_id}/{item.id}/"

    def item_guid(self, item: Reminder) -> str:
        return self.request.build_absolute_uri(
            f"/content/{item.user.user_profile.feed_id}/{item.id}/"
        )

    def item_pubdate(self, item: Reminder) -> datetime:
        return item.created_at

    def item_updateddate(self, item: Reminder) -> datetime:
        return item.updated_at
