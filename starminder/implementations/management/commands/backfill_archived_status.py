"""
Management command to backfill archived status for existing Star records.
"""

import time

import httpx
from allauth.socialaccount.models import SocialToken
from django.core.management.base import BaseCommand
from httpx_retries import Retry, RetryTransport

from starminder.content.models import Star
from starminder.core.models import CustomUser


class Command(BaseCommand):
    help = "Backfill archived status for existing Star records from GitHub API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Only process stars for specific username",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        username_filter = options.get("user")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        # Get all users with tokens
        users = CustomUser.objects.filter(socialaccount__isnull=False).distinct()
        if username_filter:
            users = users.filter(username=username_filter)

        total_users = users.count()
        self.stdout.write(f"Processing {total_users} user(s)...")

        total_stars = 0
        total_updated = 0
        total_errors = 0

        for user_idx, user in enumerate(users, 1):
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n[{user_idx}/{total_users}] Processing user: {user.username}"
                )
            )

            try:
                # Get user's token
                token = SocialToken.objects.filter(account__user=user).first()
                if not token:
                    self.stdout.write(
                        self.style.WARNING(f"  No token found for {user.username}")
                    )
                    continue

                # Get all Star records for this user (via reminders)
                stars = list(Star.objects.filter(reminder__user=user))
                star_count = len(stars)
                total_stars += star_count

                if star_count == 0:
                    self.stdout.write("  No Star records found")
                    continue

                self.stdout.write(f"  Found {star_count} Star records")

                # Initialize GitHub API client
                httpx_transport = RetryTransport(
                    retry=Retry(total=5, backoff_factor=0.5)
                )

                updated_count = 0
                error_count = 0

                with httpx.Client(transport=httpx_transport) as client:
                    # For each Star record, query GitHub API for archived status
                    for star_idx, star in enumerate(stars, 1):
                        full_name = f"{star.owner}/{star.name}"

                        try:
                            # Query individual repo via GitHub API
                            response = client.get(
                                f"https://api.github.com/repos/{star.owner}/{star.name}",
                                headers={
                                    "Accept": "application/vnd.github+json",
                                    "Authorization": f"Bearer {token.token}",
                                },
                            )
                            response.raise_for_status()
                            repo_data = response.json()
                            archived_status = repo_data.get("archived", False)

                            # Update if archived
                            if archived_status:
                                if not dry_run:
                                    star.archived = archived_status
                                    star.save(update_fields=["archived"])
                                updated_count += 1

                                status = "ARCHIVED" if archived_status else "ACTIVE"
                                action = (
                                    "[DRY RUN] Would update" if dry_run else "Updated"
                                )
                                self.stdout.write(
                                    f"    [{star_idx}/{star_count}] {action}: {full_name} -> {status}"
                                )

                            else:
                                self.stdout.write(
                                    f"    [{star_idx}/{star_count}] {full_name} -> already has {archived_status}"
                                )

                        except httpx.HTTPStatusError as e:
                            if e.response.status_code == 404:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"    [{star_idx}/{star_count}] Not found: {full_name}"
                                    )
                                )
                            else:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"    [{star_idx}/{star_count}] Error fetching {full_name}: {e}"
                                    )
                                )
                            error_count += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"    [{star_idx}/{star_count}] Error processing {full_name}: {e}"
                                )
                            )
                            error_count += 1

                        # Add small delay to respect rate limits (every 10 requests)
                        if star_idx % 10 == 0 and star_idx < star_count:
                            time.sleep(0.1)

                total_updated += updated_count
                total_errors += error_count

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Completed: {updated_count} updated, {error_count} errors"
                    )
                )

                # Rate limiting between users - be nice to GitHub API
                if user_idx < total_users:
                    self.stdout.write("  Sleeping 2s before next user...")
                    time.sleep(2)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  Error processing user {user.username}: {e}")
                )
                total_errors += 1
                continue

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("BACKFILL COMPLETE"))
        self.stdout.write(f"Total users processed: {total_users}")
        self.stdout.write(f"Total Star records: {total_stars}")
        self.stdout.write(f"Total updated: {total_updated}")
        self.stdout.write(f"Total errors: {total_errors}")
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN - No actual changes made"))
        self.stdout.write("=" * 50)
