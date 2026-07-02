from http import HTTPStatus
from unittest.mock import Mock, patch

from django.template.loader import render_to_string
import pytest

from starminder.content.email import send_email
from starminder.content.models import Reminder, Star


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
def test_calls_api_with_correct_parameters(mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "test_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.OK
    mock_post.return_value = mock_response

    send_email(
        recipient="user@example.com",
        subject="Test Subject",
        html="<p>Test HTML</p>",
        text="Test text",
    )

    mock_post.assert_called_once()
    call_args = mock_post.call_args

    assert call_args[0][0] == "https://api.forwardemail.net/v1/emails"
    assert call_args[1]["json"]["from"] == "test@starminder.dev"
    assert call_args[1]["json"]["to"] == "user@example.com"
    assert call_args[1]["json"]["subject"] == "Test Subject"
    assert call_args[1]["json"]["html"] == "<p>Test HTML</p>"
    assert call_args[1]["json"]["text"] == "Test text"


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
def test_includes_authorization_header(mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "test_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.OK
    mock_post.return_value = mock_response

    send_email(
        recipient="user@example.com",
        subject="Test",
        html="<p>Test</p>",
        text="Test",
    )

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]

    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
def test_includes_content_type_header(mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "test_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.OK
    mock_post.return_value = mock_response

    send_email(
        recipient="user@example.com",
        subject="Test",
        html="<p>Test</p>",
        text="Test",
    )

    call_args = mock_post.call_args
    headers = call_args[1]["headers"]

    assert headers["Content-Type"] == "application/json"


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
@patch("starminder.content.email.logger")
def test_logs_on_success(mock_logger, mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "test_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.OK
    mock_post.return_value = mock_response

    send_email(
        recipient="user@example.com",
        subject="Test",
        html="<p>Test</p>",
        text="Test",
    )

    mock_logger.info.assert_called()
    info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
    assert any("Sending email to user@example.com" in call for call in info_calls)
    assert any("Done." in call for call in info_calls)


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
@patch("starminder.content.email.logger")
def test_logs_critical_on_failure(mock_logger, mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "test_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.BAD_REQUEST
    mock_post.return_value = mock_response

    send_email(
        recipient="user@example.com",
        subject="Test",
        html="<p>Test</p>",
        text="Test",
    )

    mock_logger.critical.assert_called_once()
    critical_call = mock_logger.critical.call_args[0][0]
    assert "Email sending failed" in critical_call


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
def test_handles_different_status_codes(mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "test_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"

    for status_code in [
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.INTERNAL_SERVER_ERROR,
    ]:
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_post.return_value = mock_response

        # Should not raise an exception
        send_email(
            recipient="user@example.com",
            subject="Test",
            html="<p>Test</p>",
            text="Test",
        )


@pytest.mark.django_db
@patch("starminder.content.email.httpx.post")
@patch("starminder.content.email.settings")
@patch("starminder.content.email.base64.b64encode")
def test_encodes_token_correctly(mock_b64encode, mock_settings, mock_post) -> None:
    mock_settings.FORWARDEMAIL_TOKEN = "my_secret_token"
    mock_settings.EMAIL_FROM = "test@starminder.dev"
    mock_b64encode.return_value.decode.return_value = "encoded_token"
    mock_response = Mock()
    mock_response.status_code = HTTPStatus.OK
    mock_post.return_value = mock_response

    send_email(
        recipient="user@example.com",
        subject="Test",
        html="<p>Test</p>",
        text="Test",
    )

    mock_b64encode.assert_called_once_with(b"my_secret_token:")


# template rendering tests for flagged project URLs


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def reminder_with_flagged_star(user):
    reminder = Reminder.objects.create(user=user)
    Star.objects.create(
        reminder=reminder,
        provider="github",
        provider_id="1",
        name="flagged-repo",
        owner="owner",
        owner_id="123",
        description="Flagged project",
        star_count=10,
        repo_url="https://github.com/owner/flagged-repo",
        project_url="https://flagged.example",
        project_url_flagged=True,
    )
    Star.objects.create(
        reminder=reminder,
        provider="github",
        provider_id="2",
        name="clean-repo",
        owner="owner",
        owner_id="123",
        description="Clean project",
        star_count=10,
        repo_url="https://github.com/owner/clean-repo",
        project_url="https://clean.example",
        project_url_flagged=False,
    )
    Star.objects.create(
        reminder=reminder,
        provider="github",
        provider_id="3",
        name="desc-flagged-repo",
        owner="owner",
        owner_id="123",
        description="Docs at flagged-desc.example for this project",
        description_flagged=True,
        star_count=10,
        repo_url="https://github.com/owner/desc-flagged-repo",
    )
    # repo_url slug deliberately differs from the name so "raw name absent"
    # assertions aren't defeated by the URL (which is safe in production)
    Star.objects.create(
        reminder=reminder,
        provider="github",
        provider_id="4",
        name="wifiphisher.org",
        name_flagged=True,
        owner="owner",
        owner_id="123",
        description="Name-flagged project",
        star_count=10,
        repo_url="https://github.com/owner/name-flagged-slug",
    )
    return reminder


@pytest.mark.django_db
def test_email_omits_flagged_project_url(user, reminder_with_flagged_star) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "https://flagged.example" not in html
    assert "https://flagged.example" not in text


@pytest.mark.django_db
def test_email_keeps_clean_project_url(user, reminder_with_flagged_star) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "https://clean.example" in html
    assert "https://clean.example" in text


@pytest.mark.django_db
def test_email_keeps_repo_url_of_flagged_star(user, reminder_with_flagged_star) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "https://github.com/owner/flagged-repo" in html
    assert "https://github.com/owner/flagged-repo" in text


@pytest.mark.django_db
def test_web_body_keeps_flagged_project_url(reminder_with_flagged_star) -> None:
    body = render_to_string(
        "_reminder_body.html", {"reminder": reminder_with_flagged_star}
    )

    assert "https://flagged.example" in body


@pytest.mark.django_db
def test_email_omits_flagged_description(user, reminder_with_flagged_star) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "flagged-desc.example" not in html
    assert "flagged-desc.example" not in text


@pytest.mark.django_db
def test_email_keeps_star_with_flagged_description(
    user, reminder_with_flagged_star
) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "desc-flagged-repo" in html
    assert "desc-flagged-repo" in text


@pytest.mark.django_db
def test_email_keeps_clean_description(user, reminder_with_flagged_star) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "Clean project" in html
    assert "Clean project" in text


@pytest.mark.django_db
def test_web_body_keeps_flagged_description(reminder_with_flagged_star) -> None:
    body = render_to_string(
        "_reminder_body.html", {"reminder": reminder_with_flagged_star}
    )

    assert "flagged-desc.example" in body


def test_emailable_name_defangs_flagged_name() -> None:
    star = Star(name="wifiphisher.org", name_flagged=True)

    assert star.emailable_name == "wifiphisher[.]org"


def test_emailable_name_keeps_unflagged_name() -> None:
    star = Star(name="cheat.sh", name_flagged=False)

    assert star.emailable_name == "cheat.sh"


def test_emailable_name_keeps_flagged_name_without_dots() -> None:
    star = Star(name="plain-repo", name_flagged=True)

    assert star.emailable_name == "plain-repo"


@pytest.mark.django_db
def test_email_defangs_flagged_name(user, reminder_with_flagged_star) -> None:
    context = {"reminder": reminder_with_flagged_star, "user": user}

    html = render_to_string("email.html", context)
    text = render_to_string("email.txt", context)

    assert "wifiphisher[.]org" in html
    assert "wifiphisher[.]org" in text
    assert "wifiphisher.org" not in html
    assert "wifiphisher.org" not in text


@pytest.mark.django_db
def test_web_body_keeps_flagged_name(reminder_with_flagged_star) -> None:
    body = render_to_string(
        "_reminder_body.html", {"reminder": reminder_with_flagged_star}
    )

    assert "wifiphisher.org" in body
    assert "wifiphisher[.]org" not in body
