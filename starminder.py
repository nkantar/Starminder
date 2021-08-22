#!/usr/bin/env python


"""Main Starminder script."""


from datetime import datetime
import random
from typing import Callable, Optional, Union

import boto3
from emoji import emojize
from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository
from jinja2 import Template
from loguru import logger
import mistune  # type: ignore

from constants import (
    AWS_ACCESS_KEY_ID,
    AWS_FROM,
    AWS_SECRET_ACCESS_KEY,
    GITHUB_FORK_URL,
    GITHUB_TOKEN,
    STARMINDER_COUNT,
    STARMINDER_RECIPIENT,
    STARMINDER_SUBJECT,
    TEMPLATE_PATH,
)


TODAY = datetime.utcnow().date().strftime("%A, %-d %B, %Y")
SUBJECT = STARMINDER_SUBJECT.substitute(today=TODAY)

StarData = list[dict[str, Optional[Union[str, int]]]]
EmailData = dict[str, Union[str, object]]
SendFunction = Callable[[str, str, str, str], None]


def gh_init() -> Github:
    """Initialize GitHub connection object."""
    logger.info("Initializing GitHub connection")
    gh = Github(GITHUB_TOKEN)
    logger.debug("Initialized GitHub connection successfully")
    return gh


def get_user(gh: Github) -> AuthenticatedUser:
    """Retrieve user for given GitHub connection object."""
    logger.info("Fetching user")
    user = gh.get_user()
    logger.debug(f"Fetched user {user.login} successfully")
    return user


def get_stars(user: AuthenticatedUser) -> list[Repository]:
    """Retrieve given user's starred repositories."""
    logger.info("Fetching stars")
    stars = list(user.get_starred())
    logger.debug(f"Fetched {len(stars)} stars successfully")
    return stars


def reconcile_count(stars: list[Repository], user_count: int) -> int:
    """Decide maximum number of stars based on setting and number of repositories."""
    logger.info("Reconciling count")
    if len(stars) >= user_count:
        logger.debug("Reconciled count to setting")
        count = user_count
    else:
        logger.debug("Reconciled count to number of stars")
        count = len(stars)
    logger.debug(f"Reconciled count: {count}")
    return count


def randomize_stars(stars: list[Repository], count: int) -> list[Repository]:
    """Retrieve random stars from given list."""
    logger.info("Randomizing stars")
    random_stars = random.sample(stars, count)
    logger.debug(f"Randomized {count} stars")
    return random_stars


def generate_star_data(stars: list[Repository]) -> StarData:
    """Generate star data for email template."""
    logger.info("Generating star email data")
    data = [
        {
            "full_name": star.full_name,
            "description": emojize(star.description or "", use_aliases=True) or None,
            "url": star.html_url,
            "homepage": star.homepage or None,
            "stargazers_count": star.stargazers_count,
            # watchers are really subscribers, thanks to GitHub API weirdness:
            # https://developer.github.com/changes/2012-09-05-watcher-api/
            "watchers_count": star.subscribers_count,
        }
        for star in stars
    ]
    logger.debug(f"Generated star email data: {data}")
    return data


def generate_name(user: AuthenticatedUser) -> str:
    """Generate user name for greeting from name and username."""
    logger.info("Generating user name")
    user_name = user.login
    if user.name:
        user_name = f"{user.name} ({user.login})"
    logger.debug(f"Generated user name: {user_name}")
    return user_name


def generate_email_data(user: AuthenticatedUser, star_data: StarData) -> EmailData:
    """Generate all data for email template."""
    logger.info("Generating email data")
    data = {
        "user_name": generate_name(user),
        "today": TODAY,
        "stars": star_data,
        "fork_url": GITHUB_FORK_URL,
    }
    logger.debug(f"Generated email data: {data}")
    return data


def generate_email_md(data: EmailData) -> str:
    """Generate raw email Markdown."""
    logger.info("Generating email Markdown")
    template = Template(TEMPLATE_PATH.read_text())
    markdown = template.render(**data)
    logger.debug(f"Generated email Markdown: {markdown}")
    return markdown


def generate_email_html(markdown: str) -> str:
    """Generate HTML email contents from Markdown."""
    logger.info("Generating email HTML")
    html: str = mistune.html(markdown)
    logger.debug(f"Generated email HTML: {html}")
    return html


def send_email(text: str, html: str, subject: str, recipient: str) -> None:
    """Send email via SES."""
    logger.info("Sending email via SES")
    client = boto3.client(
        "ses",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    email_kwargs = {
        "Source": AWS_FROM,
        "Destination": {"ToAddresses": [recipient]},
        "Message": {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
        },
        "ReplyToAddresses": [AWS_FROM],
    }
    client.send_email(**email_kwargs)
    logger.debug("Sent email via SES")


def reconcile_send_email_function() -> SendFunction:
    """Decide whether to use the built-in or custom send_email implementation."""
    logger.info("Reconciling send_email function")
    try:
        from custom import send_email as custom_send_email  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Reconciled send_email to built-in")
        send_function = send_email
    else:
        logger.debug("Reconciled send_email to custom")
        send_function = custom_send_email
    return send_function


def starminder() -> None:
    """Execute Starminder."""
    logger.info("Running Starminder")

    # auth
    gh = gh_init()
    user = get_user(gh)

    # fetch all stars
    all_stars = get_stars(user)

    # decide how many stars
    count = reconcile_count(all_stars, STARMINDER_COUNT)

    # pick stars
    random_stars = randomize_stars(all_stars, count)

    # generate email data
    star_data = generate_star_data(random_stars)
    email_data = generate_email_data(user, star_data)

    # generate email contents from template
    email_md = generate_email_md(email_data)
    email_html = generate_email_html(email_md)

    # send email
    send_email_function = reconcile_send_email_function()
    send_email_function(email_md, email_html, SUBJECT, STARMINDER_RECIPIENT)


if __name__ == "__main__":
    logger.info("Running script: %s" % __file__)
    starminder()
    logger.debug("Finished running script")
