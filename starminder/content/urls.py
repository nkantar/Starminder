from django.urls import path

from starminder.content.views import AtomFeedView, HTMLFeedView, PostDetailView

urlpatterns = [
    path("<uuid:feed_id>/", HTMLFeedView.as_view(), name="html_feed"),
    path("<uuid:feed_id>/feed", AtomFeedView(), name="atom_feed"),
    path("<uuid:feed_id>/<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
]
