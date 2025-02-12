def proportional_samples(cells: list, max_samples: int) -> list:
    """
    Calculate proportional sample numbers for cells based on their areas.

    Arguments:
        cells: List of GeoJSON rectangles
        max_samples: Maximum number of samples for the largest area

    Returns: List of sample numbers corresponding to each cell
    """

    def calculate_area(coords):
        """
        GeoJSON coordinates are in the format
        [[[lon1,lat1], [lon2,lat1], [lon2,lat2], [lon1,lat2], [lon1,lat1]]]
        """
        # Extract the lat/lon
        lon = [pt[0] for pt in coords]
        lat = [pt[1] for pt in coords]
        # Calculate width and height in deg, then approximate area (deg^2)
        return (max(lon) - min(lon)) * (max(lat) - min(lat))

    # Calculate areas for all cells
    areas = []
    for cell in cells:
        if cell["geometry"]["type"] != "Polygon":
            raise ValueError("All GeoJSON features must be Polygons")
        # Polygons can have multiple rings, we want the outer (hence [0])
        areas.append(calculate_area(cell["geometry"]["coordinates"][0]))

    # Find the maximum area for scaling
    if areas:
        max_area = max(areas)

    # Scale the area to get proportional samples, rounded to nearest int.
    # Ensure minimum of 1 sample.
    return [max(1, int(((area / max_area) * max_samples) + 0.5)) for area in areas]
