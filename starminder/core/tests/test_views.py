import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_view_returns_200(client: Client) -> None:
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
