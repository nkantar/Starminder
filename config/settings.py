from datetime import time
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
import tomlkit


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

PYPROJECT_PATH = BASE_DIR / "pyproject.toml"
PYPROJECT = tomlkit.parse(PYPROJECT_PATH.open().read())

SECRET_KEY = getenv("STARMINDER_DJANGO_SECRET_KEY")

ENVIRONMENT = getenv("STARMINDER_ENVIRONMENT")

DEBUG = bool(int(getenv("STARMINDER_DEBUG")))

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "starminder.main",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "starminder.main.middleware.EmailRequiredMiddleware",
    "starminder.main.middleware.FooterStatsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

ENVIRONMENT_DATABASES = {
    "test": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "local": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "prod": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}


DATABASES = {
    "default": ENVIRONMENT_DATABASES[ENVIRONMENT],
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

USE_I18N = False

USE_L10N = False

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]


##################################################


ADMIN_PREFIX = getenv("STARMINDER_ADMIN_PREFIX")

ENCRYPTION_KEY = getenv("STARMINDER_ENCRYPTION_KEY")

SITE_ID = 1

APPEND_SLASH = True

STARMINDER_VERSION = PYPROJECT["tool"]["poetry"]["version"]

################
# django-allauth

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

ACCOUNT_LOGOUT_ON_GET = True


##################
# Profile defaults

DEFAULT_DAY = getenv("STARMINDER_DEFAULT_DAY")
DEFAULT_TIME = time.fromisoformat(getenv("STARMINDER_DEFAULT_TIME"))
DEFAULT_NUMBER = int(getenv("STARMINDER_DEFAULT_NUMBER"))

AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
