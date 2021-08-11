#!/usr/bin/env python


from datetime import datetime
import random

import boto3
from emoji import emojize
from github import Github
from jinja2 import Template
from loguru import logger
import mistune

from constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_FROM,
    GITHUB_FORK_URL,
    GITHUB_TOKEN,
    STARMINDER_COUNT,
    STARMINDER_RECIPIENT,
    STARMINDER_SUBJECT,
    TEMPLATE_PATH,
)


TODAY = datetime.utcnow().date().strftime("%A, %-d %B, %Y")


def gh_init():
    """Initialize GitHub connection object."""
    logger.info("Initializing GitHub connection")
    gh = Github(GITHUB_TOKEN)
    logger.debug("Initilized GitHub connection successfully")
    return gh


def get_user(gh):
    """Retrieve user for given GitHub connection object."""
    logger.info("Fetching user")
    user = gh.get_user()
    logger.debug(f"Fetched user {user.login} successfully")
    return user


def get_stars(user):
    """Retrieve given user's starred repositories."""
    logger.info("Fetching stars")
    stars = list(user.get_starred())
    logger.debug(f"Fetched {len(stars)} stars successfully")
    return stars


def reconcile_count(stars):
    """Decide maximum number of stars based on setting and number of repositories."""
    logger.info("Reconciling count")
    if len(stars) >= STARMINDER_COUNT:
        logger.debug("Reconciled count to setting")
        count = STARMINDER_COUNT
    else:
        logger.debug("Reconciled count to number of stars")
        count = len(stars)
    logger.debug(f"Reconciled count: {count}")
    return count


def randomize_stars(stars):
    """Retrieve random stars from given list."""
    logger.info("Randomizing stars")
    count = reconcile_count(stars)
    random_stars = random.sample(stars, count)
    logger.debug(f"Randomized {count} stars")
    return random_stars


def generate_star_data(stars):
    """Generate star data for email template."""
    logger.info("Generating star email data")
    data = [
        {
            "full_name": star.full_name,
            "description": emojize(star.description, use_aliases=True) or None,
            "url": star.url,
            "homepage": star.homepage or None,
            "stargazers_count": star.stargazers_count,
        }
        for star in stars
    ]
    logger.debug(f"Generated star email data: {data}")
    return data


def generate_name(user):
    """Generate user name for greeting from name and username."""
    logger.info("Generating user name")
    user_name = user.login
    if user.name:
        user_name = f"{user.name} ({user.login})"
    logger.debug(f"Generated user name: {user_name}")
    return user_name


def generate_email_data(user, star_data):
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


def generate_email_md(data):
    """Generate raw email Markdown."""
    logger.info("Generating email Markdown")
    template = Template(TEMPLATE_PATH.read_text())
    markdown = template.render(**data)
    logger.debug(f"Generated email Markdown: {markdown}")
    return markdown


def generate_email_html(markdown):
    """Generate HTML email contents from Markdown."""
    logger.info("Generating email HTML")
    html = mistune.html(markdown)
    logger.debug(f"Generated email HTML: {html}")
    return html


def send_email(text, html):
    """Send email via SES."""
    logger.info("Sending email via SES")
    subject = STARMINDER_SUBJECT.substitute(today=TODAY)
    client = boto3.client(
        "ses",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    email_kwargs = {
        "Source": AWS_FROM,
        "Destination": {"ToAddresses": [STARMINDER_RECIPIENT]},
        "Message": {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
        },
        "ReplyToAddresses": [AWS_FROM],
    }
    client.send_email(**email_kwargs)
    logger.debug("Sent email via SES")


def starminder():
    """Execute Starminder."""
    logger.info("Running Starminder")

    # auth
    gh = gh_init()
    user = get_user(gh)

    # fetch all stars
    all_stars = get_stars(user)

    # pick stars
    random_stars = randomize_stars(all_stars)

    # generate email data
    star_data = generate_star_data(random_stars)
    email_data = generate_email_data(user, star_data)

    # generate email contents from template
    email_md = generate_email_md(email_data)
    email_html = generate_email_html(email_md)

    # send email
    send_email(email_md, email_html)


if __name__ == "__main__":
    logger.info("Running script: %s" % __file__)
    starminder()
    logger.debug("Finished running script")
