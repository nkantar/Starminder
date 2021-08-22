from unittest.mock import Mock

import pytest

from starminder import generate_star_data


@pytest.fixture
def full_star():
    star = Mock()
    star.full_name = "foobar/bazbarf"
    star.description = "hello :sunglasses: there"
    star.html_url = "https://example.com/github"
    star.homepage = "https://example.com/home"
    star.stargazers_count = 42
    star.subscribers_count = 13
    return star


@pytest.fixture
def empty_star():
    star = Mock()
    star.full_name = "meep/moop"
    star.description = None
    star.html_url = "https://example.com/github/meep"
    star.homepage = None
    star.stargazers_count = 0
    star.subscribers_count = 0
    return star


def test_generate_star_data(full_star, empty_star):
    star_data = generate_star_data([full_star, empty_star])
    assert star_data == [
        {
            "full_name": "foobar/bazbarf",
            "description": "hello 😎 there",
            "url": "https://example.com/github",
            "homepage": "https://example.com/home",
            "stargazers_count": 42,
            "watchers_count": 13,
        },
        {
            "full_name": "meep/moop",
            "description": None,
            "url": "https://example.com/github/meep",
            "homepage": None,
            "stargazers_count": 0,
            "watchers_count": 0,
        },
    ]
