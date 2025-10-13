import random
from datetime import datetime

from allauth.socialaccount.models import SocialToken

# from django.template.loader import render_to_string
from django_q.tasks import schedule
from loguru import logger

# from starminder.content.email import send_email
from starminder.content.models import Reminder, Star
from starminder.core.models import CustomUser, UserProfile
from starminder.implementations.getters import GETTERS


def generate_content(user_id: int) -> None:
    logger.info(f"Generating data for {user_id}")

    user = CustomUser.objects.get(id=user_id)
    logger.info(f"Found user {user.username}")

    tokens = SocialToken.objects.filter(account__user=user)
    logger.info(f"Found {len(tokens)} tokens for {user.username}")
    if not tokens:
        logger.info("Nothing to do here, exiting")
        return

    all_stars = []
    for token in tokens:
        logger.info(f"Processing {token.account.provider}…")

        provider = token.account.provider
        try:
            getter = GETTERS[provider]
        except KeyError:
            logger.critical(f"No getter found for provider: {provider}")
            continue

        stars = getter(user, token)
        logger.info(f"Found {len(stars)} stars")
        all_stars.extend(stars)

        logger.info("Processed.")

    logger.info(f"Found {len(all_stars)} stars")

    sample_size = min(user.user_profile.max_entries, len(all_stars))
    sampled_stars = random.sample(all_stars, sample_size)

    logger.info(f"Sampled {sample_size} stars")

    reminder = Reminder.objects.create(user_id=user_id)

    for star_data in sampled_stars:
        Star.objects.create(
            reminder=reminder,
            provider=token.account.provider,
            provider_id=star_data.provider_id,
            owner=star_data.owner,
            owner_id=star_data.owner_id,
            name=star_data.name,
            description=star_data.description,
            star_count=star_data.star_count,
            repo_url=star_data.repo_url,
            project_url=star_data.project_url,
        )

    # if user.email:
    #     logger.info(f"Found email for {user}, sending…")

    #     subject = f"[Starminder] {reminder.title}"
    #     html = render_to_string("email.html", {"reminder": reminder, "user": user})
    #     text = render_to_string("email.txt", {"reminder": reminder, "user": user})
    #     send_email(recipient=user.email, subject=subject, html=html, text=text)

    #     logger.info("Sent!")

    # else:
    #     logger.info(f"No email found for {user}")

    logger.info("Done!")


def start_jobs() -> None:
    logger.info("Scheduling all applicable jobs…")
    now = datetime.now()

    scheduled_profiles = UserProfile.objects.scheduled_for(now)
    logger.info(f"Found {scheduled_profiles.count()} scheduled profiles")

    for profile in scheduled_profiles:
        schedule(
            "starminder.implementations.jobs.generate_content",
            profile.user.id,
        )

    logger.info("Done!")
