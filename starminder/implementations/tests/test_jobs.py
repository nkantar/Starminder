from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from django.utils import timezone
import pytest
from allauth.socialaccount.models import SocialAccount, SocialToken

from starminder.content.models import Reminder, Star
from starminder.core.models import UserProfile
from starminder.implementations.jobs import (
    cleanup_temp_stars,
    generate_data,
    pager,
    start_jobs,
    user_job,
)
from starminder.implementations.models import TempStar


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


def backdate_reminders() -> None:
    """Age existing reminders past the duplicate-delivery guard window."""
    Reminder.objects.update(created_at=timezone.now() - timedelta(hours=2))


@pytest.fixture(autouse=True)
def mock_get_flagged_urls():
    with patch(
        "starminder.implementations.jobs.get_flagged_urls",
        return_value=set(),
    ) as mock_flagged:
        yield mock_flagged


@pytest.fixture
def temp_star(user):
    return TempStar.objects.create(
        user=user,
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


# start_jobs tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_start_jobs_schedules_matching_profiles(
    mock_datetime, mock_async_task, user, user2
) -> None:
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    user.user_profile.day_of_week = now.weekday()
    user.user_profile.hour_of_day = now.hour
    user.user_profile.save()

    user2.user_profile.day_of_week = now.weekday()
    user2.user_profile.hour_of_day = now.hour
    user2.user_profile.save()

    start_jobs()

    assert mock_async_task.call_count == 2
    scheduled_user_ids = {call[0][1] for call in mock_async_task.call_args_list}
    assert scheduled_user_ids == {user.id, user2.id}


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_start_jobs_does_not_schedule_non_matching_profiles(
    mock_datetime, mock_async_task, user
) -> None:
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    user.user_profile.day_of_week = (now.weekday() + 1) % 7
    user.user_profile.hour_of_day = now.hour
    user.user_profile.save()

    start_jobs()

    mock_async_task.assert_not_called()


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_start_jobs_schedules_every_day_profiles(
    mock_datetime, mock_async_task, user
) -> None:
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    user.user_profile.day_of_week = UserProfile.EVERY_DAY
    user.user_profile.hour_of_day = now.hour
    user.user_profile.save()

    start_jobs()

    mock_async_task.assert_called_once_with(
        "starminder.implementations.jobs.user_job",
        user.id,
    )


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_start_jobs_calls_correct_function_name(
    mock_datetime, mock_async_task, user
) -> None:
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    user.user_profile.day_of_week = now.weekday()
    user.user_profile.hour_of_day = now.hour
    user.user_profile.save()

    start_jobs()

    mock_async_task.assert_called_once_with(
        "starminder.implementations.jobs.user_job",
        user.id,
    )


# user_job tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_user_job_queues_pager_with_user_and_tokens(
    mock_async_task, user, social_token
) -> None:
    user_job(user.id)

    mock_async_task.assert_called_once()
    call_args = mock_async_task.call_args
    assert call_args[0][0] == "starminder.implementations.jobs.pager"
    assert call_args[0][1] == user
    assert len(call_args[0][2]) == 1
    assert call_args[0][2][0] == social_token


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_user_job_does_not_queue_when_no_tokens(mock_async_task, user) -> None:
    user_job(user.id)

    mock_async_task.assert_not_called()


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_user_job_handles_multiple_tokens(mock_async_task, user, social_token) -> None:
    # Create second social account and token
    social_account2 = SocialAccount.objects.create(
        user=user,
        provider="github",
        uid="test_uid_2",
    )
    social_token2 = SocialToken.objects.create(
        account=social_account2,
        token="test_token_2",
    )

    user_job(user.id)

    mock_async_task.assert_called_once()
    tokens = mock_async_task.call_args[0][2]
    assert len(tokens) == 2
    assert social_token in tokens
    assert social_token2 in tokens


# pager tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_creates_temp_stars_from_api_response(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 123,
            "name": "repo1",
            "owner": {"login": "owner1", "id": 456},
            "description": "Test repo",
            "stargazers_count": 100,
            "html_url": "https://github.com/owner1/repo1",
            "homepage": "https://example.com",
        }
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token])

    assert TempStar.objects.filter(user=user).count() == 1
    temp_star = TempStar.objects.get(user=user)
    assert temp_star.provider == "github"
    assert temp_star.provider_id == "123"
    assert temp_star.name == "repo1"
    assert temp_star.owner == "owner1"
    assert temp_star.owner_id == "456"
    assert temp_star.description == "Test repo"
    assert temp_star.star_count == 100
    assert temp_star.repo_url == "https://github.com/owner1/repo1"
    assert temp_star.project_url == "https://example.com"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_schedules_next_page_when_100_items(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": i,
            "name": f"repo{i}",
            "owner": {"login": "owner", "id": 1},
            "stargazers_count": 10,
            "html_url": "https://github.com/owner/repo",
        }
        for i in range(100)
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token], page=1)

    mock_async_task.assert_called_once()
    call_args = mock_async_task.call_args
    assert call_args[0][0] == "starminder.implementations.jobs.pager"
    assert call_args[0][1] == user
    assert call_args[0][2] == [social_token]
    assert call_args[0][3] == 2


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_schedules_next_token_when_partial_page(
    mock_client_class, mock_async_task, user
) -> None:
    token1 = SocialToken.objects.create(
        account=SocialAccount.objects.create(user=user, provider="github", uid="uid1"),
        token="token1",
    )
    token2 = SocialToken.objects.create(
        account=SocialAccount.objects.create(user=user, provider="github", uid="uid2"),
        token="token2",
    )

    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "name": "repo1",
            "owner": {"login": "owner", "id": 1},
            "stargazers_count": 10,
            "html_url": "https://github.com/owner/repo",
        }
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [token1, token2], page=1)

    mock_async_task.assert_called_once()
    call_args = mock_async_task.call_args
    assert call_args[0][0] == "starminder.implementations.jobs.pager"
    assert call_args[0][1] == user
    assert call_args[0][2] == [token2]
    assert call_args[0][3] == 1


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_schedules_generate_data_when_last_token(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "name": "repo1",
            "owner": {"login": "owner", "id": 1},
            "stargazers_count": 10,
            "html_url": "https://github.com/owner/repo",
        }
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token], page=1)

    mock_async_task.assert_called_once()
    call_args = mock_async_task.call_args
    assert call_args[0][0] == "starminder.implementations.jobs.generate_data"
    assert call_args[0][1] == user.id
    assert call_args[0][2] == "test_uid"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_calls_github_api_with_correct_headers(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token], page=1)

    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args
    assert call_args[0][0] == "https://api.github.com/user/starred"
    assert call_args[1]["headers"]["Accept"] == "application/vnd.github+json"
    assert call_args[1]["headers"]["Authorization"] == f"Bearer {social_token.token}"
    assert call_args[1]["params"]["per_page"] == 100
    assert call_args[1]["params"]["page"] == 1


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_handles_null_description_and_project_url(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 123,
            "name": "repo1",
            "owner": {"login": "owner1", "id": 456},
            "description": None,
            "stargazers_count": 100,
            "html_url": "https://github.com/owner1/repo1",
            "homepage": None,
        }
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token])

    temp_star = TempStar.objects.get(user=user)
    assert temp_star.description is None
    assert temp_star.project_url is None


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_skips_repos_with_deleted_owner(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 123,
            "name": "repo1",
            "owner": {"login": "owner1", "id": 456},
            "stargazers_count": 100,
            "html_url": "https://github.com/owner1/repo1",
        },
        {
            "id": 124,
            "name": "deleted-repo",
            "owner": None,
            "stargazers_count": 50,
            "html_url": "https://github.com/deleted-user/deleted-repo",
        },
        {
            "id": 125,
            "name": "repo2",
            "owner": {"login": "owner2", "id": 789},
            "stargazers_count": 200,
            "html_url": "https://github.com/owner2/repo2",
        },
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token])

    assert TempStar.objects.filter(user=user).count() == 2
    temp_stars = TempStar.objects.filter(user=user).order_by("provider_id")
    assert temp_stars[0].name == "repo1"
    assert temp_stars[1].name == "repo2"


# generate_data tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_creates_reminder(mock_async_task, user, temp_star) -> None:
    generate_data(user.id, "irrelevant")

    assert Reminder.objects.filter(user=user).count() == 1


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_creates_stars_from_temp_stars(
    mock_async_task, user, temp_star
) -> None:
    generate_data(user.id, "irrelevant")

    reminder = Reminder.objects.get(user=user)
    assert Star.objects.filter(reminder=reminder).count() == 1

    star = Star.objects.get(reminder=reminder)
    assert star.provider == temp_star.provider
    assert star.provider_id == temp_star.provider_id
    assert star.name == temp_star.name
    assert star.owner == temp_star.owner
    assert star.owner_id == temp_star.owner_id
    assert star.description == temp_star.description
    assert star.star_count == temp_star.star_count
    assert star.repo_url == temp_star.repo_url
    assert star.project_url == temp_star.project_url


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_respects_max_entries_limit(mock_async_task, user) -> None:
    # Create 10 temp stars
    for i in range(10):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    user.user_profile.max_entries = 3
    user.user_profile.save()

    generate_data(user.id, "irrelevant")

    reminder = Reminder.objects.get(user=user)
    assert Star.objects.filter(reminder=reminder).count() == 3


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_create_reminder_when_no_temp_stars(
    mock_async_task, user
) -> None:
    generate_data(user.id, "irrelevant")

    assert Reminder.objects.filter(user=user).count() == 0


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.render_to_string")
def test_generate_data_queues_email_when_email_configured(
    mock_render, mock_async_task, user, temp_star
) -> None:
    mock_render.return_value = "rendered content"

    user.user_profile.reminder_email = "user@example.com"
    user.user_profile.save()

    generate_data(user.id, "irrelevant")

    # Should have 2 calls: one for email send, one for cleanup
    assert mock_async_task.call_count == 2

    # Check email send call
    email_call = mock_async_task.call_args_list[0]
    assert email_call[0][0] == "starminder.content.email.send_email"
    assert email_call[1]["recipient"] == "user@example.com"
    assert "☆ Starminder ☆" in email_call[1]["subject"]


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_queue_email_when_no_email(
    mock_async_task, user, temp_star
) -> None:
    user.user_profile.reminder_email = None
    user.user_profile.save()

    generate_data(user.id, "irrelevant")

    # Should only have 1 call for cleanup
    assert mock_async_task.call_count == 1
    assert (
        mock_async_task.call_args[0][0]
        == "starminder.implementations.jobs.cleanup_temp_stars"
    )


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_queues_cleanup(mock_async_task, user, temp_star) -> None:
    generate_data(user.id, "irrelevant")

    # Get the last call (cleanup should be last)
    cleanup_call = mock_async_task.call_args_list[-1]
    assert cleanup_call[0][0] == "starminder.implementations.jobs.cleanup_temp_stars"
    assert cleanup_call[0][1] == user.id


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.random.sample")
def test_generate_data_samples_randomly(mock_sample, mock_async_task, user) -> None:
    temp_stars = []
    for i in range(10):
        temp_stars.append(
            TempStar.objects.create(
                user=user,
                provider="github",
                provider_id=str(i),
                name=f"repo{i}",
                owner="owner",
                owner_id="123",
                star_count=10,
                repo_url=f"https://github.com/owner/repo{i}",
            )
        )

    user.user_profile.max_entries = 5
    user.user_profile.save()

    mock_sample.return_value = temp_stars[:5]

    generate_data(user.id, "irrelevant")

    mock_sample.assert_called_once()
    assert len(mock_sample.call_args[0][0]) == 10
    assert mock_sample.call_args[0][1] == 5


# cleanup_temp_stars tests


@pytest.mark.django_db
def test_cleanup_temp_stars_deletes_user_temp_stars(user, temp_star) -> None:
    assert TempStar.objects.filter(user=user).count() == 1

    cleanup_temp_stars(user.id)

    assert TempStar.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_cleanup_temp_stars_only_deletes_specific_user(user, user2) -> None:
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="repo1",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/repo1",
    )
    TempStar.objects.create(
        user=user2,
        provider="github",
        provider_id="2",
        name="repo2",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/repo2",
    )

    cleanup_temp_stars(user.id)

    assert TempStar.objects.filter(user=user).count() == 0
    assert TempStar.objects.filter(user=user2).count() == 1


@pytest.mark.django_db
def test_cleanup_temp_stars_deletes_multiple_temp_stars(user) -> None:
    for i in range(5):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    assert TempStar.objects.filter(user=user).count() == 5

    cleanup_temp_stars(user.id)

    assert TempStar.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_cleanup_temp_stars_handles_no_temp_stars(user) -> None:
    cleanup_temp_stars(user.id)

    assert TempStar.objects.filter(user=user).count() == 0


# archived repository tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_captures_archived_status(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    """Test that pager captures archived field from GitHub API."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 123,
            "name": "active-repo",
            "owner": {"login": "owner1", "id": 456},
            "description": "Active repo",
            "stargazers_count": 100,
            "html_url": "https://github.com/owner1/active-repo",
            "archived": False,
        },
        {
            "id": 124,
            "name": "archived-repo",
            "owner": {"login": "owner2", "id": 789},
            "description": "Archived repo",
            "stargazers_count": 50,
            "html_url": "https://github.com/owner2/archived-repo",
            "archived": True,
        },
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token])

    temp_stars = TempStar.objects.filter(user=user).order_by("provider_id")
    assert temp_stars.count() == 2
    assert temp_stars[0].archived is False
    assert temp_stars[1].archived is True


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.httpx.Client")
def test_pager_defaults_archived_to_false_when_missing(
    mock_client_class, mock_async_task, user, social_token
) -> None:
    """Test that pager defaults archived to False if not in API response."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 123,
            "name": "repo-without-archived",
            "owner": {"login": "owner1", "id": 456},
            "stargazers_count": 100,
            "html_url": "https://github.com/owner1/repo-without-archived",
        }
    ]
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    pager(user, [social_token])

    temp_star = TempStar.objects.get(user=user)
    assert temp_star.archived is False


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_excludes_archived_when_preference_false(
    mock_async_task, user
) -> None:
    """Test that archived repos are excluded when include_archived is False."""
    # Set user preference to exclude archived
    user.user_profile.include_archived = False
    user.user_profile.save()

    # Create mix of archived and non-archived TempStars
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="active-repo",
        owner="owner",
        owner_id="123",
        star_count=100,
        repo_url="https://github.com/owner/active-repo",
        archived=False,
    )
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="2",
        name="archived-repo",
        owner="owner",
        owner_id="123",
        star_count=50,
        repo_url="https://github.com/owner/archived-repo",
        archived=True,
    )

    generate_data(user.id, "irrelevant")

    # Verify only non-archived repo appears in results
    reminder = Reminder.objects.get(user=user)
    stars = Star.objects.filter(reminder=reminder)
    assert stars.count() == 1
    assert stars[0].archived is False
    assert stars[0].name == "active-repo"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_includes_archived_by_default(mock_async_task, user) -> None:
    """Test that archived repos are included when include_archived is True (default)."""
    # Default is include_archived=True
    assert user.user_profile.include_archived is True

    # Create archived TempStar
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="archived-repo",
        owner="owner",
        owner_id="123",
        star_count=50,
        repo_url="https://github.com/owner/archived-repo",
        archived=True,
    )

    generate_data(user.id, "irrelevant")

    # Verify archived repo appears in results
    reminder = Reminder.objects.get(user=user)
    stars = Star.objects.filter(reminder=reminder)
    assert stars.count() == 1
    assert stars[0].archived is True
    assert stars[0].name == "archived-repo"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_preserves_archived_status_in_stars(
    mock_async_task, user
) -> None:
    """Test that archived status is correctly copied from TempStar to Star."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="active-repo",
        owner="owner",
        owner_id="123",
        star_count=100,
        repo_url="https://github.com/owner/active-repo",
        archived=False,
    )
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="2",
        name="archived-repo",
        owner="owner",
        owner_id="123",
        star_count=50,
        repo_url="https://github.com/owner/archived-repo",
        archived=True,
    )

    generate_data(user.id, "irrelevant")

    reminder = Reminder.objects.get(user=user)
    stars = Star.objects.filter(reminder=reminder).order_by("name")
    assert stars.count() == 2
    assert stars[0].name == "active-repo"
    assert stars[0].archived is False
    assert stars[1].name == "archived-repo"
    assert stars[1].archived is True


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_handles_all_archived_when_excluded(
    mock_async_task, user
) -> None:
    """Test that no reminder is created when all repos are archived and excluded."""
    user.user_profile.include_archived = False
    user.user_profile.save()

    # Create only archived TempStars
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="archived-repo-1",
        owner="owner",
        owner_id="123",
        star_count=50,
        repo_url="https://github.com/owner/archived-repo-1",
        archived=True,
    )
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="2",
        name="archived-repo-2",
        owner="owner",
        owner_id="123",
        star_count=25,
        repo_url="https://github.com/owner/archived-repo-2",
        archived=True,
    )

    generate_data(user.id, "irrelevant")

    # No reminder should be created
    assert Reminder.objects.filter(user=user).count() == 0


# own repository tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_includes_own_when_preference_false(
    mock_async_task,
    user,
) -> None:
    """Test that own repositories are excluded when setting is False."""

    user.user_profile.include_own = False
    user.user_profile.save()

    # create mix of own and non-own TempStars
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="active-repo",
        owner="owner",
        owner_id="123",
        star_count=100,
        repo_url="https://github.com/owner/active-repo",
        archived=False,
    )
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="2",
        name="archived-repo",
        owner="owner",
        owner_id="123",
        star_count=50,
        repo_url="https://github.com/owner/archived-repo",
        archived=True,
    )
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="3",
        name="active-repo-2",
        owner=user.username,
        owner_id="456",
        star_count=100,
        repo_url="https://github.com/456/active-repo-2",
        archived=False,
    )
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="4",
        name="archived-repo",
        owner=user.username,
        owner_id="456",
        star_count=50,
        repo_url="https://github.com/456/archived-repo-3",
        archived=True,
    )

    generate_data(user.id, "456")

    # verify only non-own repos appear in results
    reminder = Reminder.objects.get(user=user)
    stars = Star.objects.filter(reminder=reminder)
    assert stars.count() == 2
    user_uids = {star.owner_id for star in stars}
    assert "456" not in user_uids


# cycle tracking tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_cycle_tracking_with_one_to_one_field(mock_async_task, user) -> None:
    """Test that cycle tracking works correctly with OneToOneField to Star."""
    for i in range(10):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    user.user_profile.max_entries = 5
    user.user_profile.save()

    generate_data(user.id, "irrelevant")

    user.user_profile.refresh_from_db()
    assert user.user_profile.cycle_start is not None

    reminder1 = Reminder.objects.first()
    assert reminder1 is not None
    reminder1_ids = set(reminder1.star_set.values_list("provider_id", flat=True))
    assert len(reminder1_ids) == 5

    backdate_reminders()

    TempStar.objects.all().delete()
    for i in range(10):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    generate_data(user.id, "irrelevant")

    user.user_profile.refresh_from_db()
    assert user.user_profile.cycle_start is None

    reminder2 = Reminder.objects.order_by("created_at")[1]
    reminder2_ids = set(reminder2.star_set.values_list("provider_id", flat=True))
    assert len(reminder2_ids) == 5

    assert len(reminder1_ids & reminder2_ids) == 0


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_cycle_cutoff_mid_reminder(mock_async_task, user) -> None:
    """Test cycle reset when cutoff happens mid-reminder."""
    for i in range(10):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    user.user_profile.max_entries = 7
    user.user_profile.save()

    generate_data(user.id, "irrelevant")
    user.user_profile.refresh_from_db()
    assert user.user_profile.cycle_start is not None

    backdate_reminders()

    TempStar.objects.all().delete()
    for i in range(10):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    generate_data(user.id, "irrelevant")

    user.user_profile.refresh_from_db()
    assert user.user_profile.cycle_start is not None

    reminder2 = Reminder.objects.order_by("created_at")[1]
    stars2 = list(reminder2.star_set.order_by("id"))

    assert user.user_profile.cycle_start.id == stars2[3].id
    assert len(stars2) == 7


@pytest.mark.django_db
def test_cycle_start_validation(user, django_user_model) -> None:
    """Test that cycle_start validation rejects Stars from other users."""
    from django.core.exceptions import ValidationError

    other_user = django_user_model.objects.create_user(
        username="other", password="pass"
    )

    other_reminder = Reminder.objects.create(user=other_user)
    other_star = Star.objects.create(
        reminder=other_reminder,
        provider="github",
        provider_id="999",
        name="repo",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/repo",
    )

    user.user_profile.cycle_start = other_star

    with pytest.raises(ValidationError):
        user.user_profile.save()


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_all_repos_shown_resets_at_first_star(mock_async_task, user) -> None:
    """Test that when all repos shown, cycle resets at the first new Star."""
    for i in range(6):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    user.user_profile.max_entries = 4
    user.user_profile.save()

    generate_data(user.id, "irrelevant")
    user.user_profile.refresh_from_db()
    assert user.user_profile.cycle_start is not None

    backdate_reminders()

    TempStar.objects.all().delete()
    for i in range(6):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    generate_data(user.id, "irrelevant")
    user.user_profile.refresh_from_db()

    reminder2 = Reminder.objects.order_by("created_at")[1]
    stars2 = list(reminder2.star_set.order_by("id"))

    assert user.user_profile.cycle_start is not None
    assert user.user_profile.cycle_start.id == stars2[2].id


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_no_duplicates_in_first_cycle(mock_async_task, user) -> None:
    """Test that no duplicates appear within the first cycle."""
    for i in range(12):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
        )

    user.user_profile.max_entries = 5
    user.user_profile.save()

    all_shown_ids = set()

    for reminder_num in range(3):
        generate_data(user.id, "irrelevant")
        backdate_reminders()

        TempStar.objects.all().delete()
        for i in range(12):
            TempStar.objects.create(
                user=user,
                provider="github",
                provider_id=str(i),
                name=f"repo{i}",
                owner="owner",
                owner_id="123",
                star_count=10,
                repo_url=f"https://github.com/owner/repo{i}",
            )

        reminder = Reminder.objects.order_by("created_at")[reminder_num]
        provider_ids = set(reminder.star_set.values_list("provider_id", flat=True))

        if len(all_shown_ids) < 12:
            duplicates = all_shown_ids & provider_ids
            if len(all_shown_ids) + len(provider_ids) <= 12:
                assert len(duplicates) == 0, f"Found duplicates in cycle: {duplicates}"

        all_shown_ids.update(provider_ids)


# project URL flagging tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_flags_flagged_project_url(
    mock_async_task, user, temp_star, mock_get_flagged_urls
) -> None:
    """Test that a flagged project URL sets the flag but preserves the URL."""
    mock_get_flagged_urls.return_value = {"https://example.com"}

    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.project_url_flagged is True
    assert star.project_url == "https://example.com"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_flag_clean_project_url(
    mock_async_task, user, temp_star
) -> None:
    """Test that a clean project URL leaves the flag unset."""
    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.project_url_flagged is False
    assert star.project_url == "https://example.com"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_checks_only_sampled_project_urls(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that the checker gets one call with only the sampled stars' URLs."""
    for i in range(3):
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(i),
            name=f"repo{i}",
            owner="owner",
            owner_id="123",
            star_count=10,
            repo_url=f"https://github.com/owner/repo{i}",
            project_url=f"https://example.com/repo{i}" if i < 2 else None,
        )

    generate_data(user.id, "irrelevant")

    mock_get_flagged_urls.assert_called_once()
    checked_urls = mock_get_flagged_urls.call_args[0][0]
    assert set(checked_urls) == {
        "https://example.com/repo0",
        "https://example.com/repo1",
    }


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_flag_missing_project_url(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that stars without a project URL are never flagged."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="repo",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/repo",
    )

    generate_data(user.id, "irrelevant")

    mock_get_flagged_urls.assert_called_once_with([])
    star = Star.objects.get(reminder__user=user)
    assert star.project_url_flagged is False


# description flagging tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_flags_description_with_flagged_url(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that a description containing a flagged URL sets the flag."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="repo",
        owner="owner",
        owner_id="123",
        description="Phishing tool, see wifiphisher.org for docs",
        star_count=10,
        repo_url="https://github.com/owner/repo",
    )
    mock_get_flagged_urls.return_value = {"wifiphisher.org"}

    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.description_flagged is True
    assert star.description == "Phishing tool, see wifiphisher.org for docs"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_flag_clean_description(
    mock_async_task, user, temp_star
) -> None:
    """Test that a description with no flagged URLs leaves the flag unset."""
    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.description_flagged is False


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_checks_description_and_project_urls_together(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that description URLs join project URLs in the single batch call."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="repo",
        owner="owner",
        owner_id="123",
        description="Docs at docs.example.org",
        star_count=10,
        repo_url="https://github.com/owner/repo",
        project_url="https://example.com",
    )

    generate_data(user.id, "irrelevant")

    mock_get_flagged_urls.assert_called_once()
    checked_urls = mock_get_flagged_urls.call_args[0][0]
    assert set(checked_urls) == {"https://example.com", "docs.example.org"}


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_flag_missing_description(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that stars without a description are never flagged."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="repo",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/repo",
    )

    generate_data(user.id, "irrelevant")

    mock_get_flagged_urls.assert_called_once_with([])
    star = Star.objects.get(reminder__user=user)
    assert star.description_flagged is False


# resilience tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_user_job_deletes_leftover_temp_stars(
    mock_async_task, user, user2, social_token, temp_star
) -> None:
    """Test that a run starts from a clean slate, for the running user only."""
    TempStar.objects.create(
        user=user2,
        provider="github",
        provider_id="1",
        name="repo",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/repo",
    )

    user_job(user.id)

    assert TempStar.objects.filter(user=user).count() == 0
    assert TempStar.objects.filter(user=user2).count() == 1
    mock_async_task.assert_called_once()


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_skips_when_recent_reminder_exists(
    mock_async_task, user, temp_star
) -> None:
    """Test that a re-delivered task doesn't create a duplicate reminder."""
    Reminder.objects.create(user=user)

    generate_data(user.id, "irrelevant")

    assert Reminder.objects.filter(user=user).count() == 1
    mock_async_task.assert_not_called()


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_proceeds_when_reminder_is_old(
    mock_async_task, user, temp_star
) -> None:
    """Test that the duplicate guard doesn't block the next legitimate run."""
    Reminder.objects.create(user=user)
    backdate_reminders()

    generate_data(user.id, "irrelevant")

    assert Reminder.objects.filter(user=user).count() == 2


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_rolls_back_on_crash(mock_async_task, user, temp_star) -> None:
    """Test that a mid-run crash leaves no partial reminder behind."""
    with patch(
        "starminder.implementations.jobs.Star.objects.create",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(RuntimeError):
            generate_data(user.id, "irrelevant")

    assert Reminder.objects.filter(user=user).count() == 0
    mock_async_task.assert_not_called()


# checker failure tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_survives_checker_failure(
    mock_async_task, user, temp_star, mock_get_flagged_urls
) -> None:
    """Test that an unexpected checker crash fails closed instead of killing the job."""
    mock_get_flagged_urls.side_effect = RuntimeError("boom")

    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.project_url_flagged is True
    assert star.name_flagged is False
    assert star.description_flagged is False

    cleanup_call = mock_async_task.call_args_list[-1]
    assert cleanup_call[0][0] == "starminder.implementations.jobs.cleanup_temp_stars"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_flags_unicode_description_domain(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that bare unicode domains in descriptions reach the checker."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="repo",
        owner="owner",
        owner_id="123",
        description="докс на ドメイン.jp",
        star_count=10,
        repo_url="https://github.com/owner/repo",
    )
    mock_get_flagged_urls.return_value = {"ドメイン.jp"}

    generate_data(user.id, "irrelevant")

    mock_get_flagged_urls.assert_called_once_with(["ドメイン.jp"])
    star = Star.objects.get(reminder__user=user)
    assert star.description_flagged is True


# name flagging tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_flags_flagged_name(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that a domain-like flagged name sets the flag but stays raw."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="wifiphisher.org",
        owner="owner",
        owner_id="123",
        star_count=10,
        repo_url="https://github.com/owner/wifiphisher.org",
    )
    mock_get_flagged_urls.return_value = {"wifiphisher.org"}

    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.name_flagged is True
    assert star.name == "wifiphisher.org"


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_does_not_flag_ordinary_name(
    mock_async_task, user, temp_star, mock_get_flagged_urls
) -> None:
    """Test that a name with no domain-like tokens is never flagged."""
    generate_data(user.id, "irrelevant")

    star = Star.objects.get(reminder__user=user)
    assert star.name_flagged is False
    checked_urls = mock_get_flagged_urls.call_args[0][0]
    assert "test-repo" not in checked_urls


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
def test_generate_data_checks_name_urls_in_batch(
    mock_async_task, user, mock_get_flagged_urls
) -> None:
    """Test that name-derived URLs join the single batch call."""
    TempStar.objects.create(
        user=user,
        provider="github",
        provider_id="1",
        name="cheat.sh",
        owner="owner",
        owner_id="123",
        description="Docs at docs.example.org",
        star_count=10,
        repo_url="https://github.com/owner/cheat.sh",
        project_url="https://example.com",
    )

    generate_data(user.id, "irrelevant")

    mock_get_flagged_urls.assert_called_once()
    checked_urls = mock_get_flagged_urls.call_args[0][0]
    assert set(checked_urls) == {
        "https://example.com",
        "docs.example.org",
        "cheat.sh",
    }


# enabled flag tests


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_start_jobs_excludes_disabled_users(
    mock_datetime, mock_async_task, user, user2
) -> None:
    """Test that disabled users are excluded from scheduled jobs."""
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    # Set both users to same schedule
    user.user_profile.day_of_week = now.weekday()
    user.user_profile.hour_of_day = now.hour
    user.user_profile.enabled = True
    user.user_profile.save()

    user2.user_profile.day_of_week = now.weekday()
    user2.user_profile.hour_of_day = now.hour
    user2.user_profile.enabled = False
    user2.user_profile.save()

    start_jobs()

    # Only the enabled user should be scheduled
    mock_async_task.assert_called_once_with(
        "starminder.implementations.jobs.user_job",
        user.id,
    )


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_scheduled_for_excludes_disabled_profiles(
    mock_datetime, mock_async_task, user, user2
) -> None:
    """Test that UserProfile.objects.scheduled_for() excludes disabled users."""
    now = datetime(2025, 10, 11, 12, 0)

    # Set both users to same schedule
    user.user_profile.day_of_week = now.weekday()
    user.user_profile.hour_of_day = now.hour
    user.user_profile.enabled = True
    user.user_profile.save()

    user2.user_profile.day_of_week = now.weekday()
    user2.user_profile.hour_of_day = now.hour
    user2.user_profile.enabled = False
    user2.user_profile.save()

    scheduled_profiles = UserProfile.objects.scheduled_for(now)

    # Only the enabled user should be in the queryset
    assert scheduled_profiles.count() == 1
    first_profile = scheduled_profiles.first()
    assert first_profile is not None
    assert first_profile.user.id == user.id


@pytest.mark.django_db
def test_new_users_enabled_by_default(db, django_user_model) -> None:
    """Test that newly created users have enabled=True by default."""
    new_user = django_user_model.objects.create_user(
        username="newuser",
        email="newuser@example.com",
        password="testpass123",
    )

    # User profile should be auto-created with enabled=True
    assert new_user.user_profile.enabled is True


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_disabling_user_prevents_scheduling(
    mock_datetime, mock_async_task, user
) -> None:
    """Test that disabling a user prevents them from being scheduled."""
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    user.user_profile.day_of_week = now.weekday()
    user.user_profile.hour_of_day = now.hour
    user.user_profile.enabled = True
    user.user_profile.save()

    start_jobs()
    assert mock_async_task.call_count == 1

    # Now disable the user
    mock_async_task.reset_mock()
    user.user_profile.enabled = False
    user.user_profile.save()

    start_jobs()
    mock_async_task.assert_not_called()


@pytest.mark.django_db
@patch("starminder.implementations.jobs.async_task")
@patch("starminder.implementations.jobs.datetime")
def test_reenabling_user_allows_scheduling(
    mock_datetime, mock_async_task, user
) -> None:
    """Test that re-enabling a user allows them to be scheduled again."""
    now = datetime(2025, 10, 11, 12, 0)
    mock_datetime.now.return_value = now

    user.user_profile.day_of_week = now.weekday()
    user.user_profile.hour_of_day = now.hour
    user.user_profile.enabled = False
    user.user_profile.save()

    start_jobs()
    mock_async_task.assert_not_called()

    # Re-enable the user
    user.user_profile.enabled = True
    user.user_profile.save()

    start_jobs()
    mock_async_task.assert_called_once_with(
        "starminder.implementations.jobs.user_job",
        user.id,
    )
