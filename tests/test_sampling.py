import numpy
import pytest

from ortho_utils.sampling import proportional_samples, Sample, Zone


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

    def test_contains(self, rects):
        points = numpy.array(
            [[0, 0], [2, 0.01], [2, 2], [10, 10], [11, 10.01], [11, 11], [-5, -5]]
        )
        zone = Zone(rects[0])
        assert numpy.allclose(
            zone.contains(points),
            [False, True, True, False, False, False, False],
        )
        zone = Zone(rects[1])
        assert numpy.allclose(
            zone.contains(points),
            [False, False, False, False, True, True, False],
        )

    def test_associate(self, rects):
        samples = [
            Sample(numpy.array([2, 2]), 1.23),
            Sample(numpy.array([2.5, 2.5]), 4.56),
            Sample(numpy.array([100, 100]), 7.89),
        ]
        zone = Zone(rects[0])
        assert zone.samples == []
        zone.associate(samples)
        assert len(zone.samples) == 2
        assert samples[0] == zone.samples[0]
        assert samples[1] == zone.samples[1]

    def test_avg_samples(self, rects):
        samples = [
            Sample(numpy.array([2, 2]), 2.5),
            Sample(numpy.array([2.5, 2.5]), 7.5),
            Sample(numpy.array([100, 100]), -100),
        ]
        zone = Zone(rects[0])
        assert zone.avg_samples() is None
        zone.associate(samples)
        assert numpy.isclose(zone.avg_samples(), 5.0)


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
