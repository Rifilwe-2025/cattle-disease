"""
Utility functions for vets app.

Includes distance calculation using Haversine formula.
"""
import math
from typing import List, Tuple
from .models import Vet


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def find_nearby_vets(latitude: float, longitude: float, radius: float = 50) -> List[Vet]:
    """
    Find vets within a specified radius of a location.
    
    Args:
        latitude: Latitude of the search location
        longitude: Longitude of the search location
        radius: Search radius in kilometers (default: 50km)
    
    Returns:
        List of Vet objects sorted by distance (nearest first)
    """
    if latitude is None or longitude is None:
        return []
    
    # Get all approved and available vets with location data
    vets = Vet.objects.filter(
        is_approved=True,
        is_available=True,
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    # Calculate distance for each vet
    vets_with_distance = []
    for vet in vets:
        distance = haversine_distance(latitude, longitude, vet.latitude, vet.longitude)
        if distance <= radius:
            vets_with_distance.append((vet, distance))
    
    # Sort by distance (nearest first)
    vets_with_distance.sort(key=lambda x: x[1])
    
    # Return only the Vet objects
    return [vet for vet, distance in vets_with_distance]


def get_vet_distance(vet: Vet, latitude: float, longitude: float) -> float:
    """
    Get distance from a location to a vet.
    
    Args:
        vet: Vet object
        latitude: Latitude of the location
        longitude: Longitude of the location
    
    Returns:
        Distance in kilometers, or None if vet has no location
    """
    if not vet.has_location():
        return None
    
    return haversine_distance(latitude, longitude, vet.latitude, vet.longitude)


def find_vets_by_region(province: str, district: str = None) -> List[Tuple[Vet, float]]:
    """
    Find all approved and available vets in the same region (province/district) as the farmer.
    This ensures farmers only see vets who serve their region.
    
    Args:
        province: Province where the farmer is located
        district: District where the farmer is located (optional for more specific filtering)
    
    Returns:
        List of tuples (Vet, distance) where distance is None if GPS not available.
        Vets are sorted by: same province > has GPS > alphabetical by name
    """
    if not province:
        return []
    
    # Get all approved and available vets
    vets = Vet.objects.filter(
        is_approved=True,
        is_available=True,
    )
    
    # Filter vets who serve the farmer's province
    vets_in_region = []
    for vet in vets:
        # Check if the vet serves this province
        # provinces_served is a JSONField that contains list of provinces
        if isinstance(vet.provinces_served, list):
            # Case-insensitive comparison
            provinces_lower = [p.lower().strip() for p in vet.provinces_served]
            if province.lower().strip() in provinces_lower:
                # Calculate distance if both have GPS coordinates
                distance = None
                vets_in_region.append((vet, distance))
        elif isinstance(vet.provinces_served, str):
            # If it's a string, check if province is mentioned
            if province.lower() in vet.provinces_served.lower():
                vets_in_region.append((vet, None))
    
    # Sort: prioritize vets with location data, then alphabetically
    vets_in_region.sort(key=lambda x: (
        x[1] is None,  # Vets without location go last
        x[0].full_name.lower()  # Then alphabetically by name
    ))
    
    return vets_in_region


def find_vets_by_region_with_distance(province: str, district: str, farmer_lat: float, farmer_lon: float) -> List[Tuple[Vet, float]]:
    """
    Find all approved vets in the same region, with distance calculation if GPS available.
    
    Args:
        province: Farmer's province
        district: Farmer's district
        farmer_lat: Farmer's latitude (optional)
        farmer_lon: Farmer's longitude (optional)
    
    Returns:
        List of tuples (Vet, distance_km) sorted by distance (nearest first).
        Distance is None if GPS not available for either farmer or vet.
    """
    # Get vets in the same region
    vets_in_region = find_vets_by_region(province, district)
    
    # Calculate distances if GPS coordinates are available
    vets_with_distance = []
    for vet, _ in vets_in_region:
        distance = None
        if farmer_lat and farmer_lon and vet.has_location():
            distance = haversine_distance(farmer_lat, farmer_lon, vet.latitude, vet.longitude)
        vets_with_distance.append((vet, distance))
    
    # Sort by distance (nearest first), vets without distance go to the end
    vets_with_distance.sort(key=lambda x: (x[1] is None, x[1] if x[1] is not None else float('inf')))
    
    return vets_with_distance
