from datetime import datetime, time

import boto3
import mistune

from django.conf import settings
from django.template.loader import render_to_string

from starminder.main.models import Profile


now = datetime.utcnow()


def send_emails():
    this_day = now.weekday() + 1
    this_hour = time(now.hour, 0)

    profiles = Profile.objects.filter(day__in=[0, this_day], time=this_hour)

    for profile in profiles:
        send_email(profile)


def send_email(profile):
    today = now.date().isoformat()
    context = {"profile": profile, "today": today}

    text = render_to_string("email.md", context={"link_format": "text", **context})
    html = mistune.html(
        render_to_string(
            "email.md",
            context={
                "link_format": "markdown",
                **context,
            },
        )
    )

    recipient = profile.email
    subject = f"[Starminder] Reminders for {today}"

    if settings.DEBUG:
        recipient = f"nik+{profile.username}@nkantar.com"
        subject = f"[DEBUG] {subject}"

    ses_send(recipient, subject, text, html)


def ses_send(recipient, subject, text, html):
    client = boto3.client(
        "ses",
        region_name="us-east-1",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    email_kwargs = {
        "Source": "Starminder <notifications@starminder.xyz>",
        "Destination": {"ToAddresses": [recipient]},
        "Message": {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
        },
        "ReplyToAddresses": ["nik+starminder@nkantar.com"],
    }
    client.send_email(**email_kwargs)
