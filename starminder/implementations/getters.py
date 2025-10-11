from typing import Callable, Literal
from dataclasses import dataclass

from allauth.socialaccount.models import SocialToken
from github import Auth, Github

from starminder.core.models import CustomUser


@dataclass
class EntryData:
    provider_id: str
    owner: str
    owner_id: str
    name: str
    description: str | None
    star_count: int
    repo_url: str
    project_url: str | None


ProviderLiteral = Literal["github",]


def github_getter(user: CustomUser, token: SocialToken) -> list[EntryData]:
    auth = Auth.Token(token.token)
    g = Github(auth=auth)
    github_user = g.get_user()
    starred = list(github_user.get_starred())
    g.close()

    return [
        EntryData(
            provider_id=str(repo.id),
            owner=repo.owner.login,
            owner_id=str(repo.owner.id),
            name=repo.name,
            description=repo.description,
            star_count=repo.stargazers_count,
            repo_url=repo.html_url,
            project_url=repo.homepage,
        )
        for repo in starred
    ]


GETTERS: dict[ProviderLiteral, Callable[[CustomUser, SocialToken], list[EntryData]]] = {
    "github": github_getter,
}
