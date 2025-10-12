import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.sites.models import Site
from django.test import Client
from django.urls import reverse

from starminder.core.models import UserProfile


@pytest.mark.django_db
def test_homepage_view_returns_200(client: Client) -> None:
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
def test_faq_view_returns_200(client: Client) -> None:
    site = Site.objects.get_current()
    github_app = SocialApp.objects.create(
        provider="github",
        name="GitHub",
        client_id="test_client_id",
        secret="test_secret",
    )
    github_app.sites.add(site)

    response = client.get(reverse("faq"))
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
def test_dashboard_view_redirects_when_not_authenticated(client: Client) -> None:
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302
    assert response["Location"].startswith("/accounts/login/")


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


@pytest.mark.django_db
def test_dashboard_context_contains_user_profile(
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
    assert "user_profile" in response.context
    assert response.context["user_profile"] == user.user_profile


@pytest.mark.django_db
def test_dashboard_context_contains_page_title(
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
    assert "page_title" in response.context
    assert response.context["page_title"] == "Dashboard"


@pytest.mark.django_db
def test_dashboard_context_contains_socialaccount_list(
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
    assert "socialaccount_list" in response.context


@pytest.mark.django_db
def test_dashboard_form_has_user_profile_instance(
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
    assert "form" in response.context
    assert response.context["form"].instance == user.user_profile


@pytest.mark.django_db
def test_dashboard_form_submission_updates_profile(
    client: Client,
    django_user_model,
) -> None:
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    client.force_login(user)

    form_data = {
        "max_entries": 10,
        "day_of_week": UserProfile.FRIDAY,
        "hour_of_day": 15,
    }
    response = client.post(reverse("dashboard"), data=form_data)

    assert response.status_code == 302
    assert response["Location"] == reverse("dashboard")

    user.user_profile.refresh_from_db()
    assert user.user_profile.max_entries == 10
    assert user.user_profile.day_of_week == UserProfile.FRIDAY
    assert user.user_profile.hour_of_day == 15


@pytest.mark.django_db
def test_dashboard_form_submission_with_invalid_data(
    client: Client,
    django_user_model,
) -> None:
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    client.force_login(user)

    form_data = {
        "max_entries": 0,
        "day_of_week": UserProfile.MONDAY,
        "hour_of_day": 12,
    }
    response = client.post(reverse("dashboard"), data=form_data)

    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_testimonials_view_returns_200(client: Client) -> None:
    site = Site.objects.get_current()
    github_app = SocialApp.objects.create(
        provider="github",
        name="GitHub",
        client_id="test_client_id",
        secret="test_secret",
    )
    github_app.sites.add(site)

    response = client.get(reverse("testimonials"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_account_view_redirects_when_not_authenticated(client: Client) -> None:
    response = client.post(reverse("delete_account"))
    assert response.status_code == 302
    assert response["Location"].startswith("/accounts/login/")


@pytest.mark.django_db
def test_delete_account_view_deletes_user_and_redirects(
    client: Client,
    django_user_model,
) -> None:
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    user_id = user.id
    client.force_login(user)

    response = client.post(reverse("delete_account"))

    assert response.status_code == 302
    assert response["Location"] == reverse("homepage")
    assert not django_user_model.objects.filter(id=user_id).exists()


@pytest.mark.django_db
def test_delete_account_view_deletes_user_profile(
    client: Client,
    django_user_model,
) -> None:
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    profile_id = user.user_profile.id
    client.force_login(user)

    response = client.post(reverse("delete_account"))

    assert response.status_code == 302
    assert not UserProfile.objects.filter(id=profile_id).exists()


@pytest.mark.django_db
def test_delete_account_view_deletes_social_accounts(
    client: Client,
    django_user_model,
) -> None:
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    social_account = SocialAccount.objects.create(
        user=user,
        provider="github",
        uid="test_github_id",
    )
    social_account_id = social_account.id
    client.force_login(user)

    response = client.post(reverse("delete_account"))

    assert response.status_code == 302
    assert not SocialAccount.objects.filter(id=social_account_id).exists()
