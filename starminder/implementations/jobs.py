import random
from datetime import datetime

from allauth.socialaccount.models import SocialToken
from django_q.tasks import schedule
from loguru import logger

from starminder.content.models import Entry, Reminder
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

    all_entries = []
    for token in tokens:
        provider = token.account.provider
        try:
            getter = GETTERS[provider]
        except KeyError:
            logger.critical(f"No getter found for provider: {provider}")
            continue

        entries = getter(user, token)
        all_entries.extend(entries)

    logger.info(f"Found {len(all_entries)} entries")

    sample_size = min(user.user_profile.max_entries, len(all_entries))
    sampled_entries = random.sample(all_entries, sample_size)

    logger.info(f"Sampled {sample_size} entries")

    reminder = Reminder.objects.create(user_id=user_id)

    for entry_data in sampled_entries:
        Entry.objects.create(
            reminder=reminder,
            provider=token.account.provider,
            provider_id=entry_data.provider_id,
            owner=entry_data.owner,
            owner_id=entry_data.owner_id,
            name=entry_data.name,
            description=entry_data.description,
            star_count=entry_data.star_count,
            repo_url=entry_data.repo_url,
            project_url=entry_data.project_url,
        )

    logger.info("Done!")


def start_jobs() -> None:
    logger.info("Scheduling all applicable jobs...")
    now = datetime.now()

    scheduled_profiles = UserProfile.objects.scheduled_for(now)
    logger.info(f"Found {scheduled_profiles.count()} scheduled profiles")

    for profile in scheduled_profiles:
        schedule(
            "starminder.implementations.jobs.generate_content",
            profile.user.id,
        )

    logger.info("Done!")
