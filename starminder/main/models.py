import random

from allauth.account.signals import user_signed_up
from cryptography.fernet import Fernet
from github import Github, NamedUser, Repository

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    DateTimeField,
    Manager,
    Model,
    OneToOneField,
    PositiveIntegerField,
    TimeField,
)
from django.dispatch import receiver
from django.utils.functional import cached_property


class ProfileManager(Manager):
    @classmethod
    def create_profile(cls, token: str, user_id: int) -> "Profile":
        fernet = Fernet(settings.ENCRYPTION_KEY)
        token_encrypted = fernet.encrypt(token.encode()).decode()

        profile = Profile(token_encrypted=token_encrypted, user_id=user_id)
        profile.save()

        return profile


class Profile(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    token_encrypted = CharField(max_length=512, null=False)

    number = PositiveIntegerField(null=False, default=settings.DEFAULT_NUMBER)
    day = PositiveIntegerField(null=False, default=settings.DEFAULT_DAY)
    time = TimeField(null=False, default=settings.DEFAULT_TIME)
    html = BooleanField(null=False, default=settings.DEFAULT_HTML)

    user = OneToOneField(User, on_delete=CASCADE, null=False)

    objects = ProfileManager()

    @property
    def token(self) -> str:
        fernet = Fernet(settings.ENCRYPTION_KEY)
        return fernet.decrypt(self.token_encrypted.encode()).decode()

    @property
    def email(self) -> str:
        return self.user.email

    @email.setter
    def email(self, new_email: str) -> None:
        self.user.email = new_email
        self.user.save()

    @property
    def username(self) -> str:
        return self.user.username

    @cached_property
    def gh_user(self) -> NamedUser:
        gh = Github(self.token)
        return gh.get_user(self.username)

    @cached_property
    def all_starred(self) -> list[Repository]:
        return list(self.gh_user.get_starred())

    @cached_property
    def max_number(self) -> int:
        if self.number < len(self.all_starred):
            return self.number
        return len(self.all_starred)

    @cached_property
    def random_starred(self) -> list[Repository]:
        return random.sample(population=self.all_starred, k=self.max_number)


@receiver(user_signed_up)
def create_profile_on_signup(request, user, signal, sender, sociallogin, **kwargs):
    Profile.objects.create_profile(token=str(sociallogin.token), user_id=user.id)
