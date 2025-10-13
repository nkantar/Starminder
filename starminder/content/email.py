from http import HTTPStatus
import base64

from django.conf import settings
import httpx
from loguru import logger


def send_email(
    recipient: str,
    subject: str,
    html: str,
    text: str,
) -> None:
    logger.info(f"Sending email to {recipient}")

    b64_token = base64.b64encode(
        f"{settings.FORWARDEMAIL_TOKEN}:".encode("utf-8")
    ).decode()

    response = httpx.post(
        "https://api.forwardemail.net/v1/emails",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {b64_token}",
        },
        json={
            "from": settings.EMAIL_FROM,
            "to": recipient,
            "subject": subject,
            "text": text,
            "html": html,
        },
    )

    if response.status_code != HTTPStatus.OK:
        logger.critical(f"Email sending failed: {response}")

    else:
        logger.info("Done.")
