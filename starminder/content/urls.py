from django.urls import path

from starminder.content.views import AtomFeedView, ReminderDetailView, ReminderListView

urlpatterns = [
    path("<uuid:feed_id>/", ReminderListView.as_view(), name="reminder_list"),
    path("<uuid:feed_id>/feed", AtomFeedView(), name="atom_feed"),
    path(
        "<uuid:feed_id>/<int:reminder_id>/",
        ReminderDetailView.as_view(),
        name="reminder_detail",
    ),
]
