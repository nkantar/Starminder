import httpx
from django.conf import settings
from loguru import logger


PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"


def send_push_notification(message: str, title: str | None = None) -> bool:
    """
    Send a push notification via Pushover API.

    Args:
        message: The message content to send
        title: Optional title for the notification

    Returns:
        True if notification was sent successfully, False otherwise
    """
    data = {
        "token": settings.PUSHOVER_API_TOKEN,
        "user": settings.PUSHOVER_USER_KEY,
        "message": message,
    }

    if title:
        data["title"] = title

    try:
        response = httpx.post(PUSHOVER_API_URL, data=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Pushover notification sent: {title or message[:50]}")
        return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to send Pushover notification: {e}")
        return False
