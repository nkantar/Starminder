from dataclasses import dataclass

from github import Auth, Github
from github.Repository import Repository

from starminder.implementations.base import BaseImplementation, EntryData


@dataclass
class GitHubImplementation(BaseImplementation):
    def retrieve_all_entries(self) -> list[Repository]:
        auth = Auth.Token(self.access_token)
        g = Github(auth=auth)
        user = g.get_user()
        starred = list(user.get_starred())
        g.close()
        return starred

    def populate_entries(self, entries: list[Repository]) -> list[EntryData]:
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
            for repo in entries
        ]
