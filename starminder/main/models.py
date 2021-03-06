import random

from github import Github, NamedUser, Repository

from django.contrib.auth import User
from django.db.models import (
    CharField,
    DateTimeField,
    ForeignKey,
    Manager,
    Model,
    PositiveIntegerField,
    TimeField,
)
from django.utils.functional import cached_property

from starminder.main.encryption import decrypt, encrypt


class ProfileManager(Manager):
    @classmethod
    def create_user(
        cls,
        username: str,
        email: str,
        token: str,
        day: int,
        time: str,
    ) -> "Profile":
        user = User(
            username=username,
            email=email,
            password="",  # ignore, setting unusable immediately after
        )
        user.set_unusable_password()
        user.save()

        profile = Profile(
            token_encrypted=encrypt(token),
            day=day,
            time=time,
            user=user,
        )
        profile.save()

        return profile


class Profile(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    token_encrypted = CharField(max_length=512, null=False)

    day = PositiveIntegerField(null=False)
    time = TimeField(null=False)
    number = PositiveIntegerField(null=False)

    user = ForeignKey(User, null=False)

    objects = ProfileManager()

    @property
    def token(self) -> str:
        return decrypt(self.token_encrypted)

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
