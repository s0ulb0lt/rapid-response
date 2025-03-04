import numpy as np
from shapely.geometry import Polygon, Point
import math

def load_polygon_from_file(file_path):
    points = []
    with open(file_path, 'r') as f:
        for line in f:
            lat, lon = map(float, line.strip().split())
            points.append((lat, lon))
    return points

def meters_to_lat_lon(meters, latitude, is_latitude=True):
    """
    Converts meters to degrees of latitude or longitude at the given latitude.
    """
    if is_latitude:
        return meters / 111320  # Convert meters to latitude degrees
    else:
        # Longitude conversion depends on latitude
        return meters / (111320 * math.cos(math.radians(latitude)))  # Convert meters to longitude degrees

def create_coverage_path(polygon_points, grid_spacing_meters=10):
    # Convert the points to a Shapely polygon object
    polygon = Polygon(polygon_points)
    
    # Get the bounding box of the polygon
    minx, miny, maxx, maxy = polygon.bounds

    # Use the average latitude for better approximation of longitude spacing
    average_lat = (miny + maxy) / 2

    # Convert grid spacing from meters to degrees
    grid_spacing_lat = meters_to_lat_lon(grid_spacing_meters, average_lat, is_latitude=True)
    grid_spacing_lon = meters_to_lat_lon(grid_spacing_meters, average_lat, is_latitude=False)

    # Create horizontal grid lines within the bounds of the polygon
    path = []
    y = miny
    while y <= maxy:
        line = []
        # Create a horizontal line from minx to maxx at y
        for x in np.arange(minx, maxx, grid_spacing_lon):
            point = Point(x, y)
            # Check if the point is inside the polygon
            if polygon.contains(point):
                line.append((y, x))  # Reverse the order (lat, lon)
        if line:
            path.append(line)
        y += grid_spacing_lat

    return path

def main():
    # Load the polygon from the file
    file_path = 'polygon.txt'
    polygon_points = load_polygon_from_file(file_path)
    
    # Generate the coverage path with a grid spacing of 100 meters
    path = create_coverage_path(polygon_points, grid_spacing_meters=100)
    
    # Print the coverage path
    for line in path:
        for point in line:
            print(point)
