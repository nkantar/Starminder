import sys
from pathlib import Path
import tomllib
from typing import cast

import dj_database_url
from dotenv import load_dotenv
from loguru import logger
import parsenvy
import sentry_sdk


load_dotenv()

logger.remove()
logger.add(sys.stdout)


DEBUG = parsenvy.bool("DJANGO_DEBUG")

SENTRY_DSN = parsenvy.str("SENTRY_DSN")

if not DEBUG:
    sentry_sdk.init(dsn=SENTRY_DSN, send_default_pii=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = parsenvy.str("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = parsenvy.list("DJANGO_ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in cast(list, ALLOWED_HOSTS)]

AUTH_USER_MODEL = "core.CustomUser"

AUTHENTICATION_BACKENDS = [
    # built-in
    "django.contrib.auth.backends.ModelBackend",
    # third-party
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_EMAIL_VERIFICATION = "none"

INSTALLED_APPS = [
    # built-in
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "django_q",
    # local
    "starminder.content",
    "starminder.core",
    "starminder.implementations",
]

MIDDLEWARE = [
    # built-in
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # third-party
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "starminder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # built-in
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                # local
                "starminder.core.context_processors.global_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "starminder.wsgi.application"

if not DEBUG:
    DATABASE_URL = parsenvy.str("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL improperly configured")
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

LOGIN_REDIRECT_URL = "/dashboard"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
if DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

SOCIALACCOUNT_STORE_TOKENS = True

ADMIN_PREFIX = parsenvy.str("DJANGO_ADMIN_PREFIX", "")

Q_CLUSTER = {
    "name": "starminder",
    "workers": 2,
    "orm": "default",
    "retry": 90,
    "timeout": 60,
}

DJANGO_SITE_DOMAIN_NAME = parsenvy.str("DJANGO_SITE_DOMAIN_NAME")
DJANGO_SITE_DISPLAY_NAME = parsenvy.str("DJANGO_SITE_DISPLAY_NAME")

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STARMINDER_VERSION = None
PYPROJECT_TOML_PATH = BASE_DIR / "pyproject.toml"
PYPROJECT_TOML_DATA = tomllib.loads(PYPROJECT_TOML_PATH.read_text())
STARMINDER_VERSION = PYPROJECT_TOML_DATA["project"]["version"]

MAILTRAP_TOKEN = parsenvy.str("MAILTRAP_TOKEN")
