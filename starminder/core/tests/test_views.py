import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.sites.models import Site
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_view_returns_200(client: Client) -> None:
    # Create a SocialApp for GitHub to allow the provider_login_url tag to work
    site = Site.objects.get_current()
    github_app = SocialApp.objects.create(
        provider="github",
        name="GitHub",
        client_id="test_client_id",
        secret="test_secret",
    )
    github_app.sites.add(site)

    response = client.get(reverse("homepage"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_view_returns_200_when_authenticated(
    client: Client,
    django_user_model,
) -> None:
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    client.force_login(user)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_shows_user_social_accounts_only(
    client: Client,
    django_user_model,
) -> None:
    user1 = django_user_model.objects.create_user(
        username="user1",
        email="user1@example.com",
        password="testpass123",
    )
    user2 = django_user_model.objects.create_user(
        username="user2",
        email="user2@example.com",
        password="testpass123",
    )

    account1 = SocialAccount.objects.create(
        user=user1,
        provider="github",
        uid="user1_github_id",
    )
    account2 = SocialAccount.objects.create(
        user=user2,
        provider="github",
        uid="user2_github_id",
    )

    client.force_login(user1)
    response = client.get(reverse("dashboard"))

    assert response.status_code == 200
    assert str(account1) in response.content.decode()
    assert str(account2) not in response.content.decode()
