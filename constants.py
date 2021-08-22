"""Starminder constants."""


import os
from pathlib import Path
from string import Template

from dotenv import load_dotenv


load_dotenv()  # helps with local dev


TEMPLATE_PATH = Path.cwd() / "email.md"

STARMINDER_COUNT = int(os.getenv("STARMINDER_COUNT", 0))
STARMINDER_RECIPIENT = os.getenv("STARMINDER_RECIPIENT", "")
STARMINDER_SUBJECT = Template("[Starminder] Reminders for $today")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_FROM = os.getenv("AWS_FROM", "")

GITHUB_TOKEN = os.getenv("GH_TOKEN", "")
GITHUB_SERVER_URL = os.getenv("GITHUB_SERVER_URL", "")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "")
GITHUB_FORK_URL = f"{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}"
