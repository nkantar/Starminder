from unittest.mock import MagicMock, patch

import pytest
from allauth.socialaccount.models import SocialAccount, SocialToken

from starminder.implementations.getters import StarData, github_getter


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def social_account(user):
    return SocialAccount.objects.create(
        user=user,
        provider="github",
        uid="test_uid",
    )


@pytest.fixture
def social_token(social_account):
    return SocialToken.objects.create(
        account=social_account,
        token="test_token",
    )


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.id = 12345
    repo.owner.login = "test-owner"
    repo.owner.id = 67890
    repo.name = "test-repo"
    repo.description = "Test repository description"
    repo.stargazers_count = 100
    repo.html_url = "https://github.com/test-owner/test-repo"
    repo.homepage = "https://example.com"
    return repo


@pytest.fixture
def mock_repo_no_description():
    repo = MagicMock()
    repo.id = 54321
    repo.owner.login = "another-owner"
    repo.owner.id = 98765
    repo.name = "another-repo"
    repo.description = None
    repo.stargazers_count = 50
    repo.html_url = "https://github.com/another-owner/another-repo"
    repo.homepage = None
    return repo


@pytest.mark.django_db
class TestStarData:
    def test_creates_with_all_fields(self):
        star_data = StarData(
            provider_id="123",
            owner="owner",
            owner_id="456",
            name="repo",
            description="A test repo",
            star_count=100,
            repo_url="https://github.com/owner/repo",
            project_url="https://example.com",
        )

        assert star_data.provider_id == "123"
        assert star_data.owner == "owner"
        assert star_data.owner_id == "456"
        assert star_data.name == "repo"
        assert star_data.description == "A test repo"
        assert star_data.star_count == 100
        assert star_data.repo_url == "https://github.com/owner/repo"
        assert star_data.project_url == "https://example.com"

    def test_creates_with_none_description(self):
        star_data = StarData(
            provider_id="123",
            owner="owner",
            owner_id="456",
            name="repo",
            description=None,
            star_count=100,
            repo_url="https://github.com/owner/repo",
            project_url="https://example.com",
        )

        assert star_data.description is None

    def test_creates_with_none_project_url(self):
        star_data = StarData(
            provider_id="123",
            owner="owner",
            owner_id="456",
            name="repo",
            description="A test repo",
            star_count=100,
            repo_url="https://github.com/owner/repo",
            project_url=None,
        )

        assert star_data.project_url is None


@pytest.mark.django_db
class TestGithubGetter:
    def test_returns_star_data_list(self, user, social_token, mock_repo):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = [mock_repo]

            result = github_getter(user, social_token)

            assert len(result) == 1
            assert isinstance(result[0], StarData)

    def test_maps_repo_data_correctly(self, user, social_token, mock_repo):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = [mock_repo]

            result = github_getter(user, social_token)

            star_data = result[0]
            assert star_data.provider_id == "12345"
            assert star_data.owner == "test-owner"
            assert star_data.owner_id == "67890"
            assert star_data.name == "test-repo"
            assert star_data.description == "Test repository description"
            assert star_data.star_count == 100
            assert star_data.repo_url == "https://github.com/test-owner/test-repo"
            assert star_data.project_url == "https://example.com"

    def test_handles_none_description(
        self, user, social_token, mock_repo_no_description
    ):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = [mock_repo_no_description]

            result = github_getter(user, social_token)

            assert result[0].description is None

    def test_handles_none_homepage(self, user, social_token, mock_repo_no_description):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = [mock_repo_no_description]

            result = github_getter(user, social_token)

            assert result[0].project_url is None

    def test_handles_multiple_repos(
        self, user, social_token, mock_repo, mock_repo_no_description
    ):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = [
                mock_repo,
                mock_repo_no_description,
            ]

            result = github_getter(user, social_token)

            assert len(result) == 2
            assert result[0].provider_id == "12345"
            assert result[1].provider_id == "54321"

    def test_handles_empty_starred_list(self, user, social_token):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = []

            result = github_getter(user, social_token)

            assert result == []

    def test_creates_auth_with_token(self, user, social_token):
        with (
            patch("starminder.implementations.getters.Auth") as mock_auth,
            patch("starminder.implementations.getters.Github") as mock_github,
        ):
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = []

            github_getter(user, social_token)

            mock_auth.Token.assert_called_once_with("test_token")

    def test_closes_github_connection(self, user, social_token):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = []

            github_getter(user, social_token)

            mock_github_instance.close.assert_called_once()

    def test_calls_get_user_on_github_instance(self, user, social_token):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = []

            github_getter(user, social_token)

            mock_github_instance.get_user.assert_called_once()

    def test_calls_get_starred_on_github_user(self, user, social_token):
        with patch("starminder.implementations.getters.Github") as mock_github:
            mock_github_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_github_user = MagicMock()
            mock_github_instance.get_user.return_value = mock_github_user
            mock_github_user.get_starred.return_value = []

            github_getter(user, social_token)

            mock_github_user.get_starred.assert_called_once()
