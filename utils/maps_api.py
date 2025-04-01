"""
Utilities for interacting with the Google Maps API.
"""
import numpy as np
import googlemaps
from typing import List, Dict, Any, Tuple


def initialize_gmaps(api_key: str) -> googlemaps.Client:
    """
    Initialize the Google Maps client using the provided API key.

    Args:
        api_key: Google Maps API key
        
    Returns:
        Initialized Google Maps client
    """
    return googlemaps.Client(key=api_key)


def generate_time_matrix(gmaps: googlemaps.Client, addresses: List[str], departure_time: int) -> np.ndarray:
    """
    Generate a time matrix with the travel times between each pair of addresses.

    Args:
        gmaps: Google Maps client
        addresses: List of addresses
        departure_time: Departure time in timestamp format
        
    Returns:
        2D matrix where each element represents the travel time (in minutes) between addresses
    """
    num_addresses = len(addresses)
    matrix = np.zeros((num_addresses, num_addresses))
    
    for i in range(num_addresses):
        for j in range(num_addresses):
            if i != j:
                directions = gmaps.directions(
                    addresses[i],
                    addresses[j],
                    mode='driving',
                    departure_time=departure_time,
                    traffic_model='best_guess'
                )
                if directions and 'legs' in directions[0] and 'duration_in_traffic' in directions[0]['legs'][0]:
                    travel_time = directions[0]['legs'][0]['duration_in_traffic']['value'] // 60  # in minutes
                    matrix[i][j] = travel_time
    
    return matrix


def generate_google_maps_url(path: List[int], addresses: List[str], gmaps: googlemaps.Client) -> str:
    """
    Generate a Google Maps URL for the route.

    Args:
        path: List of location indices in order
        addresses: List of address strings
        gmaps: Google Maps client
        
    Returns:
        URL for Google Maps route
    """
    route_coordinates = []
    for i in path:
        location = gmaps.geocode(addresses[i])[0]['geometry']['location']
        route_coordinates.append((location['lat'], location['lng']))
    
    google_maps_url = 'https://www.google.com/maps/dir/'
    for coord in route_coordinates:
        google_maps_url += f'{coord[0]},{coord[1]}/'
    
    # Add return to starting point
    google_maps_url += f'{route_coordinates[0][0]},{route_coordinates[0][1]}/'
    return google_maps_url


def get_geocoded_locations(gmaps: googlemaps.Client, addresses: List[str]) -> List[Dict[str, float]]:
    """
    Get the latitude and longitude for each address.
    
    Args:
        gmaps: Google Maps client
        addresses: List of address strings
        
    Returns:
        List of dictionaries with lat/lng coordinates
    """
    locations = []
    for address in addresses:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            locations.append({
                'lat': location['lat'],
                'lng': location['lng']
            })
        else:
            # If geocoding fails, add None
            locations.append(None)
    
    return locations
