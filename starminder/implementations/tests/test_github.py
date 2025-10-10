from unittest.mock import MagicMock, Mock, patch

from starminder.implementations.base import EntryData
from starminder.implementations.github import GitHubImplementation


@patch("starminder.implementations.github.Github")
@patch("starminder.implementations.github.Auth")
def test_retrieve_all_entries(mock_auth: MagicMock, mock_github: MagicMock) -> None:
    mock_repo1 = Mock()
    mock_repo2 = Mock()

    mock_github_instance = Mock()
    mock_user = Mock()
    mock_starred = MagicMock()
    mock_starred.__iter__ = Mock(return_value=iter([mock_repo1, mock_repo2]))

    mock_user.get_starred.return_value = mock_starred
    mock_github_instance.get_user.return_value = mock_user
    mock_github.return_value = mock_github_instance

    implementation = GitHubImplementation(access_token="test_token")
    result = implementation.retrieve_all_entries()

    mock_auth.Token.assert_called_once_with("test_token")
    mock_github_instance.get_user.assert_called_once()
    mock_user.get_starred.assert_called_once()
    mock_github_instance.close.assert_called_once()
    assert result == [mock_repo1, mock_repo2]


def test_populate_entries() -> None:
    implementation = GitHubImplementation(access_token="test_token")

    mock_repo1 = Mock()
    mock_repo1.id = 123
    mock_repo1.owner.login = "owner1"
    mock_repo1.owner.id = 1001
    mock_repo1.name = "repo1"
    mock_repo1.description = "Description 1"
    mock_repo1.stargazers_count = 100
    mock_repo1.html_url = "https://github.com/owner1/repo1"
    mock_repo1.homepage = "https://homepage1.com"

    mock_repo2 = Mock()
    mock_repo2.id = 456
    mock_repo2.owner.login = "owner2"
    mock_repo2.owner.id = 1002
    mock_repo2.name = "repo2"
    mock_repo2.description = None
    mock_repo2.stargazers_count = 50
    mock_repo2.html_url = "https://github.com/owner2/repo2"
    mock_repo2.homepage = None

    result = implementation.populate_entries([mock_repo1, mock_repo2])

    assert len(result) == 2
    assert all(isinstance(entry, EntryData) for entry in result)

    assert result[0].owner == "owner1"
    assert result[0].name == "repo1"
    assert result[0].description == "Description 1"
    assert result[0].star_count == 100
    assert result[0].repo_url == "https://github.com/owner1/repo1"
    assert result[0].project_url == "https://homepage1.com"

    assert result[1].owner == "owner2"
    assert result[1].name == "repo2"
    assert result[1].description is None
    assert result[1].star_count == 50
    assert result[1].repo_url == "https://github.com/owner2/repo2"
    assert result[1].project_url is None


@patch.object(GitHubImplementation, "retrieve_all_entries")
def test_generate_entries(mock_retrieve: MagicMock) -> None:
    mock_repo1 = Mock()
    mock_repo1.id = 123
    mock_repo1.owner.login = "owner1"
    mock_repo1.owner.id = 1001
    mock_repo1.name = "repo1"
    mock_repo1.description = "Description 1"
    mock_repo1.stargazers_count = 100
    mock_repo1.html_url = "https://github.com/owner1/repo1"
    mock_repo1.homepage = "https://homepage1.com"

    mock_repo2 = Mock()
    mock_repo2.id = 456
    mock_repo2.owner.login = "owner2"
    mock_repo2.owner.id = 1002
    mock_repo2.name = "repo2"
    mock_repo2.description = None
    mock_repo2.stargazers_count = 50
    mock_repo2.html_url = "https://github.com/owner2/repo2"
    mock_repo2.homepage = None

    mock_retrieve.return_value = [mock_repo1, mock_repo2]

    implementation = GitHubImplementation(access_token="test_token")
    result = implementation.generate_entries()

    assert len(result) == 2
    assert all(isinstance(entry, EntryData) for entry in result)

    owners = {entry.owner for entry in result}
    assert owners == {"owner1", "owner2"}

    for entry in result:
        if entry.owner == "owner1":
            assert entry.name == "repo1"
            assert entry.description == "Description 1"
            assert entry.star_count == 100
            assert entry.repo_url == "https://github.com/owner1/repo1"
            assert entry.project_url == "https://homepage1.com"
        elif entry.owner == "owner2":
            assert entry.name == "repo2"
            assert entry.description is None
            assert entry.star_count == 50
            assert entry.repo_url == "https://github.com/owner2/repo2"
            assert entry.project_url is None
