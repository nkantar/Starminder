from unittest.mock import Mock

import pytest

from starminder import generate_name


@pytest.fixture
def user_full():
    user = Mock()
    user.login = "baz"
    user.name = "foo bar"
    return user


@pytest.fixture
def user_login_only():
    user = Mock()
    user.login = "meep"
    user.name = None
    return user


def test_full(user_full):
    name = generate_name(user_full)
    assert name == "foo bar (baz)"


def test_login_only(user_login_only):
    name = generate_name(user_login_only)
    assert name == "meep"
