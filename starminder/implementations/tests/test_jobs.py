from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from allauth.socialaccount.models import SocialAccount, SocialToken

from starminder.content.models import Reminder, Star
from starminder.core.models import UserProfile
from starminder.implementations.getters import StarData
from starminder.implementations.jobs import generate_content, start_jobs


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
def social_account(user):
    return SocialAccount.objects.create(
        user=user,
        provider="github",
        uid="test_uid",
    )


@pytest.fixture
def social_token(social_account):
    return SocialToken.objects.create(
        account=social_account,
        token="test_token",
    )


@pytest.fixture
def star_data_list():
    return [
        StarData(
            provider_id="1",
            owner="owner1",
            owner_id="101",
            name="repo1",
            description="Description 1",
            star_count=100,
            repo_url="https://github.com/owner1/repo1",
            project_url="https://example.com/1",
        ),
        StarData(
            provider_id="2",
            owner="owner2",
            owner_id="102",
            name="repo2",
            description="Description 2",
            star_count=200,
            repo_url="https://github.com/owner2/repo2",
            project_url=None,
        ),
        StarData(
            provider_id="3",
            owner="owner3",
            owner_id="103",
            name="repo3",
            description=None,
            star_count=300,
            repo_url="https://github.com/owner3/repo3",
            project_url="https://example.com/3",
        ),
    ]


@pytest.mark.django_db
class TestGenerateContent:
    def test_creates_reminder_for_user(self, user, social_token, star_data_list):
        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=star_data_list)
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            assert Reminder.objects.filter(user=user).count() == 1

    def test_creates_stars_from_getter_data(self, user, social_token, star_data_list):
        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=star_data_list)
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            reminder = Reminder.objects.get(user=user)
            stars = Star.objects.filter(reminder=reminder)
            assert stars.count() == 3

    def test_respects_max_entries_limit(self, user, social_token, star_data_list):
        user.user_profile.max_entries = 2
        user.user_profile.save()

        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=star_data_list)
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            reminder = Reminder.objects.get(user=user)
            stars = Star.objects.filter(reminder=reminder)
            assert stars.count() == 2

    def test_handles_user_with_no_tokens(self, user):
        generate_content(user.id)

        assert Reminder.objects.filter(user=user).count() == 0

    def test_handles_unknown_provider(self, user, social_account, social_token):
        social_account.provider = "unknown_provider"
        social_account.save()

        generate_content(user.id)

        assert Reminder.objects.filter(user=user).count() == 1
        reminder = Reminder.objects.get(user=user)
        assert Star.objects.filter(reminder=reminder).count() == 0

    def test_creates_star_with_correct_data(self, user, social_token, star_data_list):
        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=star_data_list[:1])
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            reminder = Reminder.objects.get(user=user)
            star = Star.objects.get(reminder=reminder)
            star_data = star_data_list[0]

            assert star.provider == "github"
            assert star.provider_id == star_data.provider_id
            assert star.owner == star_data.owner
            assert star.owner_id == star_data.owner_id
            assert star.name == star_data.name
            assert star.description == star_data.description
            assert star.star_count == star_data.star_count
            assert star.repo_url == star_data.repo_url
            assert star.project_url == star_data.project_url

    def test_handles_empty_stars_list(self, user, social_token):
        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=[])
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            reminder = Reminder.objects.get(user=user)
            assert Star.objects.filter(reminder=reminder).count() == 0

    def test_samples_randomly_from_stars(self, user, social_token):
        large_star_list = [
            StarData(
                provider_id=str(i),
                owner=f"owner{i}",
                owner_id=str(100 + i),
                name=f"repo{i}",
                description=f"Desc {i}",
                star_count=i * 10,
                repo_url=f"https://github.com/owner{i}/repo{i}",
                project_url=None,
            )
            for i in range(10)
        ]

        user.user_profile.max_entries = 5
        user.user_profile.save()

        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=large_star_list)
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            reminder = Reminder.objects.get(user=user)
            stars = Star.objects.filter(reminder=reminder)
            assert stars.count() == 5

    def test_calls_getter_with_user_and_token(self, user, social_token, star_data_list):
        with patch("starminder.implementations.jobs.GETTERS") as mock_getters:
            mock_getter = MagicMock(return_value=star_data_list)
            mock_getters.__getitem__.return_value = mock_getter

            generate_content(user.id)

            mock_getter.assert_called_once_with(user, social_token)


@pytest.mark.django_db
class TestStartJobs:
    def test_schedules_jobs_for_matching_profiles(self, user, user2):
        now = datetime(2025, 10, 11, 12, 0)
        user.user_profile.day_of_week = now.weekday()
        user.user_profile.hour_of_day = now.hour
        user.user_profile.save()

        user2.user_profile.day_of_week = now.weekday()
        user2.user_profile.hour_of_day = now.hour
        user2.user_profile.save()

        with (
            patch("starminder.implementations.jobs.datetime") as mock_datetime,
            patch("starminder.implementations.jobs.schedule") as mock_schedule,
        ):
            mock_datetime.now.return_value = now

            start_jobs()

            assert mock_schedule.call_count == 2
            scheduled_user_ids = {call[0][1] for call in mock_schedule.call_args_list}
            assert scheduled_user_ids == {user.id, user2.id}

    def test_does_not_schedule_non_matching_profiles(self, user):
        now = datetime(2025, 10, 11, 12, 0)
        user.user_profile.day_of_week = (now.weekday() + 1) % 7
        user.user_profile.hour_of_day = now.hour
        user.user_profile.save()

        with (
            patch("starminder.implementations.jobs.datetime") as mock_datetime,
            patch("starminder.implementations.jobs.schedule") as mock_schedule,
        ):
            mock_datetime.now.return_value = now

            start_jobs()

            mock_schedule.assert_not_called()

    def test_schedules_every_day_profiles(self, user):
        now = datetime(2025, 10, 11, 12, 0)
        user.user_profile.day_of_week = UserProfile.EVERY_DAY
        user.user_profile.hour_of_day = now.hour
        user.user_profile.save()

        with (
            patch("starminder.implementations.jobs.datetime") as mock_datetime,
            patch("starminder.implementations.jobs.schedule") as mock_schedule,
        ):
            mock_datetime.now.return_value = now

            start_jobs()

            mock_schedule.assert_called_once()
            assert mock_schedule.call_args[0][1] == user.id

    def test_calls_schedule_with_correct_function_name(self, user):
        now = datetime(2025, 10, 11, 12, 0)
        user.user_profile.day_of_week = now.weekday()
        user.user_profile.hour_of_day = now.hour
        user.user_profile.save()

        with (
            patch("starminder.implementations.jobs.datetime") as mock_datetime,
            patch("starminder.implementations.jobs.schedule") as mock_schedule,
        ):
            mock_datetime.now.return_value = now

            start_jobs()

            mock_schedule.assert_called_once_with(
                "starminder.implementations.jobs.generate_content",
                user.id,
            )

    def test_handles_no_scheduled_profiles(self):
        now = datetime(2025, 10, 11, 12, 0)

        with (
            patch("starminder.implementations.jobs.datetime") as mock_datetime,
            patch("starminder.implementations.jobs.schedule") as mock_schedule,
        ):
            mock_datetime.now.return_value = now

            start_jobs()

            mock_schedule.assert_not_called()

    def test_schedules_at_different_hours(self, user, user2):
        now = datetime(2025, 10, 11, 12, 0)
        user.user_profile.day_of_week = now.weekday()
        user.user_profile.hour_of_day = now.hour
        user.user_profile.save()

        user2.user_profile.day_of_week = now.weekday()
        user2.user_profile.hour_of_day = (now.hour + 1) % 24
        user2.user_profile.save()

        with (
            patch("starminder.implementations.jobs.datetime") as mock_datetime,
            patch("starminder.implementations.jobs.schedule") as mock_schedule,
        ):
            mock_datetime.now.return_value = now

            start_jobs()

            assert mock_schedule.call_count == 1
            mock_schedule.assert_called_once_with(
                "starminder.implementations.jobs.generate_content",
                user.id,
            )
