import random
from dataclasses import dataclass
from typing import Any


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


@dataclass
class BaseImplementation:
    access_token: str
    max_entries: int = 5  # TODO eventually configurable

    def retrieve_all_entries(self) -> list[Any]:
        raise NotImplementedError

    def populate_entries(self, entries: list[dict]) -> list[EntryData]:
        return [
            EntryData(
                provider_id=entry["provider_id"],
                owner=entry["owner"],
                owner_id=entry["owner_id"],
                name=entry["name"],
                description=entry["description"] if entry["description"] else None,
                star_count=entry["star_count"],
                repo_url=entry["repo_url"],
                project_url=entry["project_url"] if entry["project_url"] else None,
            )
            for entry in entries
        ]

    def generate_entries(self) -> list[EntryData]:
        entries = self.retrieve_all_entries()
        sample_size = min(self.max_entries, len(entries))
        sampled = random.sample(entries, sample_size)
        populated = self.populate_entries(sampled)
        return populated
