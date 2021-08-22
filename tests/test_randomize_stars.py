import pytest

from starminder import randomize_stars


TEST_PARAMS = [
    ([], 0),
    (["a"], 0),
    (["a"], 1),
    (["a", "b", "c"], 0),
    (["a", "b", "c"], 2),
    (["a", "b", "c"], 3),
]


@pytest.mark.parametrize("stars,count", TEST_PARAMS)
def test_randomize_stars(stars, count):
    random_stars = randomize_stars(stars, count)
    for star in random_stars:
        assert star in stars
