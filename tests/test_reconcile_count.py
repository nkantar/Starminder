import pytest

from starminder import reconcile_count


TEST_PARAMS = [
    ([], 0, 0),
    ([], 1, 0),
    ([], 3, 0),
    (["a"], 0, 0),
    (["a"], 1, 1),
    (["a"], 3, 1),
    (["a", "b"], 0, 0),
    (["a", "b"], 1, 1),
    (["a", "b"], 3, 2),
]


@pytest.mark.parametrize("stars,count,expected", TEST_PARAMS)
def test_reconcile_count(stars, count, expected):
    count = reconcile_count(stars, count)
    assert count == expected
