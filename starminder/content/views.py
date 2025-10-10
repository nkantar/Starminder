from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.views.generic import DetailView, ListView

from starminder.content.models import Post
from starminder.core.models import UserProfile


class HTMLFeedView(ListView):
    template_name = "feed.html"
    context_object_name = "posts"

    def get_queryset(self):
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

    def get_queryset(self):
        feed_id = self.kwargs["feed_id"]
        user_profile = get_object_or_404(UserProfile, feed_id=feed_id)
        return Post.objects.filter(user=user_profile.user).prefetch_related("entry_set")


class AtomFeedView(Feed):
    feed_type = Atom1Feed

    def get_object(self, request, feed_id):
        self.request = request
        return get_object_or_404(UserProfile, feed_id=feed_id)

    def title(self, obj):
        return f"Starminder Feed - {obj.user.username}"

    def link(self, obj):
        return self.request.build_absolute_uri(f"/feeds/{obj.feed_id}/")

    def description(self, obj):
        return f"Starred repository reminders for {obj.user.username}"

    def items(self, obj):
        return (
            Post.objects.filter(user=obj.user)
            .prefetch_related("user", "entry_set")
            .order_by("-created_at")
        )

    def item_title(self, item):
        return f"Post from {item.created_at.strftime('%Y-%m-%d %H:%M')}"

    def item_description(self, item):
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

    def item_link(self, item):
        return f"/feeds/{item.user.user_profile.feed_id}/{item.id}/"

    def item_guid(self, item):
        return self.request.build_absolute_uri(
            f"/feeds/{item.user.user_profile.feed_id}/{item.id}/"
        )

    def item_pubdate(self, item):
        return item.created_at

    def item_updateddate(self, item):
        return item.updated_at
