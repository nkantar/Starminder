from unittest.mock import patch

from starminder.implementations.base import BaseImplementation, Entry


class ModifiedPopulateEntriesImplementation(BaseImplementation):
    def populate_entries(self, entries: list) -> list:
        return [
            Entry(
                owner=item.get("username"),
                name=item.get("proj_name"),
                description=item.get("desc"),
                star_count=item.get("stars"),
                repo_url=item.get("repo"),
                project_url=item.get("url"),
            )
            for item in entries
        ]


def test_populate_entries_default():
    implementation = BaseImplementation(access_token="test_token")
    test_list = [
        {
            "owner": "test_owner1",
            "name": "test_name1",
            "description": "test_desc1",
            "star_count": 10,
            "repo_url": "https://test1.com",
            "project_url": "https://project1.com",
        },
        {
            "owner": "test_owner2",
            "name": "test_name2",
            "description": None,
            "star_count": 100,
            "repo_url": "https://test.com",
            "project_url": None,
        },
    ]
    result = implementation.populate_entries(test_list)
    assert len(result) == 2
    assert all(isinstance(entry, Entry) for entry in result)

    owners = {entry.owner for entry in result}
    assert owners == {"test_owner1", "test_owner2"}

    assert result[0].owner == "test_owner1"
    assert result[0].name == "test_name1"
    assert result[0].description == "test_desc1"
    assert result[0].star_count == 10
    assert result[0].repo_url == "https://test1.com"
    assert result[0].project_url == "https://project1.com"

    assert result[1].owner == "test_owner2"
    assert result[1].name == "test_name2"
    assert result[1].description is None
    assert result[1].star_count == 100
    assert result[1].repo_url == "https://test.com"
    assert result[1].project_url is None


@patch.object(BaseImplementation, "retrieve_all_entries")
def test_generate_entries_default(mock_retrieve):
    mock_entries = [
        {
            "owner": "user1",
            "name": "repo1",
            "description": "A test repository",
            "star_count": 100,
            "repo_url": "https://github.com/user1/repo1",
            "project_url": "https://repo1.com",
        },
        {
            "owner": "user2",
            "name": "repo2",
            "description": None,
            "star_count": 50,
            "repo_url": "https://github.com/user2/repo2",
            "project_url": None,
        },
    ]
    mock_retrieve.return_value = mock_entries

    implementation = BaseImplementation(access_token="test_token")
    result = implementation.generate_entries()

    assert len(result) == 2
    assert all(isinstance(entry, Entry) for entry in result)

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
def test_generate_entries_modified_populate_entries(mock_retrieve):
    mock_entries = [
        {
            "username": "user1",
            "proj_name": "repo1",
            "desc": "A test repository",
            "stars": 100,
            "repo": "https://github.com/user1/repo1",
            "url": "https://repo1.com",
        },
        {
            "username": "user2",
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
    assert all(isinstance(entry, Entry) for entry in result)

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
