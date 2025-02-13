from collections import namedtuple
import numpy
from shapely.geometry import shape
from shapely.vectorized import contains


# Samples should be an array of lat/lon, and a density value
Sample = namedtuple("Sample", ["coordinates", "value"])


class Zone:
    """
    This class is meant to house multiple methods of turning zone polygons and
    density measurements into a measurement associated with a point.
    """

    def __init__(self, zone: dict) -> None:
        # Data checking
        if zone["geometry"]["type"] != "Polygon":
            raise ValueError("All GeoJSON features must be Polygons")
        coords = zone["geometry"]["coordinates"][0]
        if len(coords) != 5:
            raise ValueError("GeoJSON polygons must be rectangles")
        if not numpy.allclose(coords[0], coords[-1]):
            raise ValueError("Polygon points must wrap around")

        self.polygon = shape(zone["geometry"])
        self.samples = []

    @property
    def area(self):
        return self.polygon.area

    def contains(self, points: numpy.ndarray):
        """
        Arguments:
            points: (N, 2) array of (lon, lat) points
        """
        return contains(self.polygon, points[:, 0], points[:, 1])

    def associate(self, samples: list):
        """
        For points contained in this zone, add them to self.samples

        Arguments:
            samples: N length list of Sample() values
        """
        points = numpy.array([sample.coordinates for sample in samples])
        for sample, contained in zip(samples, self.contains(points)):
            if contained:
                self.samples.append(sample)

    def avg_samples(self):
        """
        Treat the density for the zone as an average, regardless of location.
        """
        if len(self.samples) == 0:
            return None
        return numpy.average([sample.value for sample in self.samples])


def proportional_samples(zones: list, max_samples: int) -> list:
    """
    Calculate proportional sample numbers for zones based on their areas.

    Arguments:
        zones: List of GeoJSON rectangles
        max_samples: Maximum number of samples for the largest area

    Returns: List of sample numbers corresponding to each zone
    """

    if len(zones) == 0:
        return []

    # Calculate areas for all zones
    areas = [Zone(zone).area for zone in zones]
    max_area = max(areas)

    # Scale the area to get proportional samples, rounded to nearest int.
    # Ensure minimum of 1 sample.
    return [max(1, int(((area / max_area) * max_samples) + 0.5)) for area in areas]
