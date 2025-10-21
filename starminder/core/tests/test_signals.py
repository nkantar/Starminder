import pytest
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from unittest.mock import patch

from starminder.core.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
def test_user_profile_created_on_user_creation() -> None:
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )

    assert hasattr(user, "user_profile")
    assert isinstance(user.user_profile, UserProfile)
    assert user.user_profile.user == user


@pytest.mark.django_db
def test_user_profile_not_created_on_user_update() -> None:
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )

    user.email = "newemail@example.com"
    user.save()

    user.refresh_from_db()
    assert user.user_profile.id == user.user_profile.id
    assert UserProfile.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_multiple_users_get_separate_profiles() -> None:
    user1 = User.objects.create_user(
        username="user1",
        email="user1@example.com",
        password="testpass123",
    )
    user2 = User.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="testpass123",
    )

    assert user1.user_profile.id != user2.user_profile.id
    assert user1.user_profile.user == user1
    assert user2.user_profile.user == user2
    assert UserProfile.objects.count() == 2


@pytest.mark.django_db
@patch("starminder.core.models.schedule")
def test_user_job_kicked_off_on_user_creation(mock_schedule) -> None:
    before_creation = datetime.now()
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    after_creation = datetime.now()

    mock_schedule.assert_called_once()
    call_args = mock_schedule.call_args
    assert call_args[0][0] == "starminder.implementations.jobs.user_job"
    assert call_args[0][1] == user.id

    scheduled_time = call_args[1]["next_run"]
    expected_min = before_creation + timedelta(minutes=1)
    expected_max = after_creation + timedelta(minutes=1)
    assert expected_min <= scheduled_time <= expected_max
