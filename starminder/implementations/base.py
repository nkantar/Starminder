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
        raise NotImplementedError

    def generate_entries(self) -> list[EntryData]:
        entries = self.retrieve_all_entries()
        sample_size = min(self.max_entries, len(entries))
        sampled = random.sample(entries, sample_size)
        populated = self.populate_entries(sampled)
        return populated
