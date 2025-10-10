from typing import Any
from unittest.mock import MagicMock, patch

from starminder.implementations.base import BaseImplementation, EntryData


class ModifiedPopulateEntriesImplementation(BaseImplementation):
    def populate_entries(self, entries: list[Any]) -> list[EntryData]:
        return [
            EntryData(
                provider_id=item.get("id"),
                owner=item.get("username"),
                owner_id=item.get("user_id"),
                name=item.get("proj_name"),
                description=item.get("desc"),
                star_count=item.get("stars"),
                repo_url=item.get("repo"),
                project_url=item.get("url"),
            )
            for item in entries
        ]


@patch.object(BaseImplementation, "retrieve_all_entries")
@patch.object(BaseImplementation, "populate_entries")
def test_generate_entries_default(
    mock_populate: MagicMock, mock_retrieve: MagicMock
) -> None:
    mock_entries = [
        {
            "provider_id": "123",
            "owner": "user1",
            "owner_id": "1001",
            "name": "repo1",
            "description": "A test repository",
            "star_count": 100,
            "repo_url": "https://github.com/user1/repo1",
            "project_url": "https://repo1.com",
        },
        {
            "provider_id": "456",
            "owner": "user2",
            "owner_id": "1002",
            "name": "repo2",
            "description": None,
            "star_count": 50,
            "repo_url": "https://github.com/user2/repo2",
            "project_url": None,
        },
    ]
    mock_retrieve.return_value = mock_entries
    mock_populate.return_value = [
        EntryData(
            provider_id="123",
            owner="user1",
            owner_id="1001",
            name="repo1",
            description="A test repository",
            star_count=100,
            repo_url="https://github.com/user1/repo1",
            project_url="https://repo1.com",
        ),
        EntryData(
            provider_id="456",
            owner="user2",
            owner_id="1002",
            name="repo2",
            description=None,
            star_count=50,
            repo_url="https://github.com/user2/repo2",
            project_url=None,
        ),
    ]

    implementation = BaseImplementation(access_token="test_token")
    result = implementation.generate_entries()

    assert len(result) == 2
    assert all(isinstance(entry, EntryData) for entry in result)

    owners = {entry.owner for entry in result}
    assert owners == {"user1", "user2"}

    for entry in result:
        if entry.owner == "user1":
            assert entry.name == "repo1"
            assert entry.description == "A test repository"
            assert entry.star_count == 100
            assert entry.repo_url == "https://github.com/user1/repo1"
            assert entry.project_url == "https://repo1.com"
        elif entry.owner == "user2":
            assert entry.name == "repo2"
            assert entry.description is None
            assert entry.star_count == 50
            assert entry.repo_url == "https://github.com/user2/repo2"
            assert entry.project_url is None


@patch.object(ModifiedPopulateEntriesImplementation, "retrieve_all_entries")
def test_generate_entries_modified_populate_entries(mock_retrieve: MagicMock) -> None:
    mock_entries = [
        {
            "id": "123",
            "username": "user1",
            "user_id": "1001",
            "proj_name": "repo1",
            "desc": "A test repository",
            "stars": 100,
            "repo": "https://github.com/user1/repo1",
            "url": "https://repo1.com",
        },
        {
            "id": "456",
            "username": "user2",
            "user_id": "1002",
            "proj_name": "repo2",
            "desc": None,
            "stars": 50,
            "repo": "https://github.com/user2/repo2",
            "url": None,
        },
    ]
    mock_retrieve.return_value = mock_entries

    implementation = ModifiedPopulateEntriesImplementation(access_token="test_token")
    result = implementation.generate_entries()

    assert len(result) == 2
    assert all(isinstance(entry, EntryData) for entry in result)

    owners = {entry.owner for entry in result}
    assert owners == {"user1", "user2"}

    for entry in result:
        if entry.owner == "user1":
            assert entry.name == "repo1"
            assert entry.description == "A test repository"
            assert entry.star_count == 100
            assert entry.repo_url == "https://github.com/user1/repo1"
            assert entry.project_url == "https://repo1.com"
        elif entry.owner == "user2":
            assert entry.name == "repo2"
            assert entry.description is None
            assert entry.star_count == 50
            assert entry.repo_url == "https://github.com/user2/repo2"
            assert entry.project_url is None
