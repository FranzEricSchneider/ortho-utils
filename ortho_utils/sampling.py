import numpy
from shapely.geometry import shape


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

    @property
    def area(self):
        return self.polygon.area

    # def calculate_density(self, points: numpy.ndarray) -> list:
    #     """
    #     From the defined zones and the captured density data, subclasses should
    #     define different methods of extrapolating those measurements across
    #     space.

    #     Arguments:
    #         points:
    #     """
    #     raise NotImplementedError("Subclasses implement their own method")


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
