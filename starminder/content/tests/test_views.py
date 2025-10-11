import pytest
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.test import Client
from django.urls import reverse

from starminder.content.models import Reminder, Star


@pytest.fixture
def social_app(db):
    site = Site.objects.get_current()
    github_app = SocialApp.objects.create(
        provider="github",
        name="GitHub",
        client_id="test_client_id",
        secret="test_secret",
    )
    github_app.sites.add(site)
    return github_app


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def user2(db, django_user_model):
    return django_user_model.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="testpass123",
    )


@pytest.fixture
def reminder(user):
    return Reminder.objects.create(user=user)


@pytest.fixture
def reminder2(user):
    return Reminder.objects.create(user=user)


@pytest.fixture
def other_user_reminder(user2):
    return Reminder.objects.create(user=user2)


@pytest.fixture
def star(reminder):
    return Star.objects.create(
        reminder=reminder,
        provider="github",
        provider_id="12345",
        name="test-repo",
        owner="test-owner",
        owner_id="67890",
        description="Test repository",
        star_count=100,
        repo_url="https://github.com/test-owner/test-repo",
        project_url="https://example.com",
    )


@pytest.mark.django_db
class TestReminderListView:
    def test_returns_200_for_valid_feed_id(self, client: Client, user, social_app):
        url = reverse("reminder_list", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_404_for_invalid_feed_id(self, client: Client, social_app):
        url = reverse(
            "reminder_list", kwargs={"feed_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_shows_only_user_reminders(
        self, client: Client, user, reminder, reminder2, other_user_reminder, social_app
    ):
        url = reverse("reminder_list", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        reminders = list(response.context["reminders"])
        assert reminder in reminders
        assert reminder2 in reminders
        assert other_user_reminder not in reminders

    def test_orders_reminders_by_created_at_desc(
        self, client: Client, user, reminder, reminder2, social_app
    ):
        url = reverse("reminder_list", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        reminders = list(response.context["reminders"])
        assert reminders[0].created_at >= reminders[1].created_at

    def test_context_contains_page_title(self, client: Client, user, social_app):
        url = reverse("reminder_list", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["page_title"] == "Reminders"

    def test_empty_reminders_list(self, client: Client, user, social_app):
        url = reverse("reminder_list", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        assert list(response.context["reminders"]) == []


@pytest.mark.django_db
class TestReminderDetailView:
    def test_returns_200_for_valid_reminder(
        self, client: Client, user, reminder, social_app
    ):
        url = reverse(
            "reminder_detail",
            kwargs={"feed_id": user.user_profile.feed_id, "reminder_id": reminder.id},
        )
        response = client.get(url)
        assert response.status_code == 200

    def test_returns_404_for_invalid_feed_id(
        self, client: Client, reminder, social_app
    ):
        url = reverse(
            "reminder_detail",
            kwargs={
                "feed_id": "00000000-0000-0000-0000-000000000000",
                "reminder_id": reminder.id,
            },
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_returns_404_for_other_user_reminder(
        self, client: Client, user, other_user_reminder, social_app
    ):
        url = reverse(
            "reminder_detail",
            kwargs={
                "feed_id": user.user_profile.feed_id,
                "reminder_id": other_user_reminder.id,
            },
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_shows_correct_reminder(self, client: Client, user, reminder, social_app):
        url = reverse(
            "reminder_detail",
            kwargs={"feed_id": user.user_profile.feed_id, "reminder_id": reminder.id},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["reminder"] == reminder

    def test_reminder_includes_stars(
        self, client: Client, user, reminder, star, social_app
    ):
        url = reverse(
            "reminder_detail",
            kwargs={"feed_id": user.user_profile.feed_id, "reminder_id": reminder.id},
        )
        response = client.get(url)

        assert response.status_code == 200
        reminder_obj = response.context["reminder"]
        stars = list(reminder_obj.star_set.all())
        assert star in stars


@pytest.mark.django_db
class TestAtomFeedView:
    def test_returns_200_for_valid_feed_id(self, client: Client, user):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"].startswith("application/atom+xml")

    def test_returns_404_for_invalid_feed_id(self, client: Client):
        url = reverse(
            "atom_feed", kwargs={"feed_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_feed_title_includes_username(self, client: Client, user):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert f"Starminder Feed - {user.username}" in content

    def test_feed_contains_user_reminders(self, client: Client, user, reminder):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "Reminder from" in content

    def test_feed_item_includes_star_information(
        self, client: Client, user, reminder, star
    ):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert star.owner in content
        assert star.name in content
        assert star.provider in content
        assert star.repo_url in content

    def test_feed_item_without_stars(self, client: Client, user, reminder):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "No stars in this reminder" in content

    def test_feed_shows_only_user_reminders(
        self, client: Client, user, user2, reminder, other_user_reminder
    ):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert f"/feeds/{user.user_profile.feed_id}/{reminder.id}/" in content
        assert (
            f"/feeds/{user2.user_profile.feed_id}/{other_user_reminder.id}/"
            not in content
        )

    def test_feed_orders_reminders_by_created_at_desc(
        self, client: Client, user, reminder, reminder2
    ):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        feed_link1 = f"/feeds/{user.user_profile.feed_id}/{reminder.id}/"
        feed_link2 = f"/feeds/{user.user_profile.feed_id}/{reminder2.id}/"
        pos1 = content.find(feed_link1)
        pos2 = content.find(feed_link2)
        assert pos2 < pos1

    def test_feed_item_with_project_url(self, client: Client, user, reminder, star):
        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert star.project_url in content

    def test_feed_item_without_project_url(self, client: Client, user, reminder):
        star_without_project = Star.objects.create(
            reminder=reminder,
            provider="github",
            provider_id="99999",
            name="test-repo-2",
            owner="test-owner-2",
            owner_id="88888",
            description="Another repo",
            star_count=50,
            repo_url="https://github.com/test-owner-2/test-repo-2",
            project_url=None,
        )

        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert star_without_project.repo_url in content

    def test_feed_item_without_description(self, client: Client, user, reminder):
        star_without_desc = Star.objects.create(
            reminder=reminder,
            provider="github",
            provider_id="77777",
            name="test-repo-3",
            owner="test-owner-3",
            owner_id="66666",
            description=None,
            star_count=25,
            repo_url="https://github.com/test-owner-3/test-repo-3",
        )

        url = reverse("atom_feed", kwargs={"feed_id": user.user_profile.feed_id})
        response = client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert star_without_desc.name in content
