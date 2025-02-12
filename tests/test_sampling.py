import pytest

from ortho_utils.sampling import proportional_samples, Zone


@pytest.fixture
def rects():
    """
    Returns two simple rectangular GeoJSON features:
    - rect1: width=4, height=3 => area=12
    - rect2: width=3, height=2 => area=6
    """
    rect1 = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [4, 0], [4, 3], [0, 3], [0, 0]]],
        },
    }
    rect2 = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[10, 10], [13, 10], [13, 12], [10, 12], [10, 10]]],
        },
    }
    return [rect1, rect2]


class TestZone:
    def test_type_error(self, rects):
        rects[0]["geometry"]["type"] = "Point"
        with pytest.raises(ValueError):
            Zone(rects[0])

    def test_non_quadrilateral_error(self, rects):
        rects[0]["geometry"]["coordinates"] = [
            [[0, 0], [4, 0], [5, 0], [4, 3], [0, 3], [0, 0]]
        ]
        with pytest.raises(ValueError):
            Zone(rects[0])

    def test_non_wrap_error(self, rects):
        rects[0]["geometry"]["coordinates"] = [[[0, 0], [4, 0], [4, 3], [0, 3], [2, 2]]]
        with pytest.raises(ValueError):
            Zone(rects[0])

    def test_area(self, rects):
        assert Zone(rects[0]).area == 12
        assert Zone(rects[1]).area == 6


class TestProportionalSamples:
    def test_basic(self, rects):
        """
        Test that the function returns the expected proportional samples:
        - rect1 area = 12
        - rect2 area = 6
        With max_samples=100, rect1 should get 100 and rect2 50.
        """
        result = proportional_samples(rects, max_samples=100)
        assert len(result) == 2
        assert result[0] == 100
        assert result[1] == 50, f"Expected 50, got {result[1]}"

    def test_empty_list(self):
        """When given an empty list, should return an empty list."""
        result = proportional_samples([], 100)
        assert result == []
