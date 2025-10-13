from django.conf import settings
from loguru import logger

from mailtrap import Address, Mail, MailtrapClient


def send_email(
    recipient: str,
    subject: str,
    html: str,
    text: str,
) -> None:
    mail = Mail(
        sender=Address(email="hello@starminder.dev", name="Starminder"),
        # reply_to=Address(email="nik+starminder@nkantar.com", name="Nik Kantar"),
        to=[Address(email=recipient)],
        subject=subject,
        html=html,
        text=text,
        category="Integration Test",
    )

    client = MailtrapClient(token=settings.MAILTRAP_TOKEN)
    response = client.send(mail)

    logger.info(response)
