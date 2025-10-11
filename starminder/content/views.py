from datetime import datetime

from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.views.generic import DetailView, ListView

from starminder.content.models import Post
from starminder.core.models import UserProfile


class ReminderListView(ListView):
    template_name = "reminder_list.html"
    context_object_name = "posts"
    extra_context = {"page_title": "Reminders"}

    def get_queryset(self) -> QuerySet[Post]:
        feed_id = self.kwargs["feed_id"]
        user_profile = get_object_or_404(UserProfile, feed_id=feed_id)
        return (
            Post.objects.filter(user=user_profile.user)
            .prefetch_related("entry_set")
            .order_by("-created_at")
        )


class PostDetailView(DetailView):
    template_name = "post.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"

    def get_queryset(self) -> QuerySet[Post]:
        feed_id = self.kwargs["feed_id"]
        user_profile = get_object_or_404(UserProfile, feed_id=feed_id)
        return Post.objects.filter(user=user_profile.user).prefetch_related("entry_set")


class AtomFeedView(Feed):
    feed_type = Atom1Feed

    def get_object(self, request: HttpRequest, feed_id: str) -> UserProfile:
        self.request = request
        return get_object_or_404(UserProfile, feed_id=feed_id)

    def title(self, obj: UserProfile) -> str:
        return f"Starminder Feed - {obj.user.username}"

    def link(self, obj: UserProfile) -> str:
        return self.request.build_absolute_uri(f"/feeds/{obj.feed_id}/")

    def description(self, obj: UserProfile) -> str:
        return f"Starred repository reminders for {obj.user.username}"

    def items(self, obj: UserProfile) -> QuerySet[Post]:
        return (
            Post.objects.filter(user=obj.user)
            .prefetch_related("user", "entry_set")
            .order_by("-created_at")
        )

    def item_title(self, item: Post) -> str:
        return f"Post from {item.created_at.strftime('%Y-%m-%d %H:%M')}"

    def item_description(self, item: Post) -> str:
        entries = item.entry_set.all()
        if not entries:
            return "No entries in this post."

        lines = []
        for entry in entries:
            lines.append(f"<h3>{entry.owner}/{entry.name} ({entry.provider})</h3>")
            if entry.description:
                lines.append(f"<p>{entry.description}</p>")
            lines.append(f"<p>Stars: {entry.star_count}</p>")
            lines.append(f'<p><a href="{entry.repo_url}">Repository</a>')
            if entry.project_url:
                lines.append(f' | <a href="{entry.project_url}">Project</a>')
            lines.append("</p>")

        return "\n".join(lines)

    def item_link(self, item: Post) -> str:
        return f"/feeds/{item.user.user_profile.feed_id}/{item.id}/"

    def item_guid(self, item: Post) -> str:
        return self.request.build_absolute_uri(
            f"/feeds/{item.user.user_profile.feed_id}/{item.id}/"
        )

    def item_pubdate(self, item: Post) -> datetime:
        return item.created_at

    def item_updateddate(self, item: Post) -> datetime:
        return item.updated_at
