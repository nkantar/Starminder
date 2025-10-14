import random
from datetime import datetime

import httpx
from httpx_retries import Retry, RetryTransport
from allauth.socialaccount.models import SocialToken
from django.template.loader import render_to_string
from django_q.tasks import async_task
from loguru import logger

from starminder.content.models import Reminder, Star
from starminder.core.models import CustomUser, UserProfile
from starminder.implementations.models import TempStar


def start_jobs() -> None:
    """Find all profiles scheduled for current hour and queue user_job for each."""
    logger.info("Scheduling all applicable jobs…")

    scheduled_profiles = UserProfile.objects.scheduled_for(datetime.now())
    logger.info(f"Found {len(scheduled_profiles)} scheduled profiles")

    for profile in scheduled_profiles:
        async_task(
            "starminder.implementations.jobs.user_job",
            profile.user.id,
        )

    logger.info("Done!")


def user_job(user_id: int) -> None:
    """Fetch user and tokens, queue pager."""
    logger.info(f"Processing user job for {user_id=}")

    user = CustomUser.objects.get(id=user_id)
    logger.info(f"Found user {user.username}")

    tokens = list(SocialToken.objects.filter(account__user=user))
    logger.info(f"Found {len(tokens)} tokens for {user.username}")

    if not tokens:
        logger.info("No tokens found, exiting")
        return

    async_task(
        "starminder.implementations.jobs.pager",
        user,
        tokens,
    )


def pager(
    user: CustomUser,
    tokens: list[SocialToken],
    page: int = 1,
) -> None:
    """Fetch starred repos from GitHub API and create TempStar objects."""
    logger.info(f"Pager for {user.username}, page {page}, {len(tokens)} tokens")

    current_token = tokens[0]

    httpx_transport = RetryTransport(retry=Retry(total=5, backoff_factor=0.5))
    with httpx.Client(transport=httpx_transport) as client:
        response = client.get(
            "https://api.github.com/user/starred",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {current_token.token}",
            },
            params={
                "per_page": 100,
                "page": page,
            },
        )
    response.raise_for_status()
    items = response.json()

    logger.info(f"Received {len(items)} items from GitHub API")

    for item in items:
        TempStar.objects.create(
            user=user,
            provider="github",
            provider_id=str(item["id"]),
            name=item["name"],
            owner=item["owner"]["login"],
            owner_id=str(item["owner"]["id"]),
            description=item.get("description"),
            star_count=item["stargazers_count"],
            repo_url=item["html_url"],
            project_url=item.get("homepage"),
        )

    # no way to know if there are more pages without trying
    if len(items) == 100:
        logger.info("Scheduling next page")
        async_task(
            "starminder.implementations.jobs.pager",
            user,
            tokens,
            page + 1,
        )

    # partial page means no more pages for this token
    elif len(tokens) > 1:
        logger.info("Scheduling next token")
        async_task(
            "starminder.implementations.jobs.pager",
            user,
            tokens[1:],
            1,
        )

    # no more tokens means we're done, queue generate_data
    else:
        logger.info("All pages processed, scheduling generate_data")
        async_task(
            "starminder.implementations.jobs.generate_data",
            user.id,
        )


def generate_data(user_id: int) -> None:
    """Sample TempStars, create Reminder and Stars, queue email sending, clean up."""
    logger.info(f"Generating data for user_id={user_id}")

    user = CustomUser.objects.get(id=user_id)
    logger.info(f"Found user {user.username}")

    temp_stars = list(TempStar.objects.filter(user=user))
    logger.info(f"Found {len(temp_stars)} temp stars")

    if not temp_stars:
        logger.info("No temp stars found, exiting")
        return

    sample_size = min(user.user_profile.max_entries, len(temp_stars))
    sampled_temp_stars = random.sample(temp_stars, sample_size)

    logger.info(f"Sampled {sample_size} temp stars")

    reminder = Reminder.objects.create(user_id=user_id)

    for temp_star in sampled_temp_stars:
        Star.objects.create(
            reminder=reminder,
            provider=temp_star.provider,
            provider_id=temp_star.provider_id,
            owner=temp_star.owner,
            owner_id=temp_star.owner_id,
            name=temp_star.name,
            description=temp_star.description,
            star_count=temp_star.star_count,
            repo_url=temp_star.repo_url,
            project_url=temp_star.project_url,
        )

    logger.info("Created reminder and stars")

    if user.user_profile.reminder_email:
        logger.info(f"Found email for {user}, queuing email send…")

        subject = f"[Starminder] {reminder.title}"
        html = render_to_string("email.html", {"reminder": reminder, "user": user})
        text = render_to_string("email.txt", {"reminder": reminder, "user": user})

        async_task(
            "starminder.content.email.send_email",
            recipient=user.user_profile.reminder_email,
            subject=subject,
            html=html,
            text=text,
        )
        logger.info("Queued email send")

    else:
        logger.info(f"No email found for {user}")

    async_task(
        "starminder.implementations.jobs.cleanup_temp_stars",
        user_id,
    )

    logger.info("Done!")


def cleanup_temp_stars(user_id: int) -> None:
    """Delete all temporary stars for a specific user."""
    logger.info(f"Cleaning up temp stars for {user_id=}")

    deleted_count, _ = TempStar.objects.filter(user_id=user_id).delete()
    logger.info(f"Deleted {deleted_count} temp stars")
