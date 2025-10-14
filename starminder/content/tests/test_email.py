from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest

from starminder.content.email import send_email


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
