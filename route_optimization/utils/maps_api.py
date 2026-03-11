"""Google Maps API utilities for fetching travel time data."""

import googlemaps
import numpy as np

from route_optimization.core.exceptions import MapsAPIError, ValidationError
from route_optimization.core.logging import get_logger

log = get_logger(__name__)


def initialize_gmaps(api_key: str) -> googlemaps.Client:
    """
    Create and return a Google Maps API client.

    Args:
        api_key: A valid Google Maps API key.

    Raises:
        ValidationError: If the API key is empty.
    """
    if not api_key:
        raise ValidationError("GOOGLE_MAPS_API_KEY is required")
    return googlemaps.Client(key=api_key)


def generate_time_matrix(
    gmaps: googlemaps.Client,
    addresses: list[str],
    departure_time: int,
) -> np.ndarray:
    """
    Build an N×N travel-time matrix (in minutes) for the given addresses.

    Uses real-time traffic data via the Google Maps Directions API.

    Args:
        gmaps: Initialized Google Maps client.
        addresses: Ordered list of address strings.
        departure_time: Unix timestamp of the planned departure.

    Returns:
        Square numpy array where ``matrix[i][j]`` is the travel time in minutes
        from address *i* to address *j*. Diagonal is 0. Missing routes are ``inf``.

    Raises:
        ValidationError: If fewer than 2 addresses are provided.
        MapsAPIError: If the API call fails for any address pair.
    """
    if len(addresses) < 2:
        raise ValidationError("at least 2 addresses are required to build a time matrix")

    n = len(addresses)
    matrix = np.zeros((n, n))

    log.info("fetching_time_matrix", num_addresses=n)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            try:
                result = gmaps.directions(
                    addresses[i],
                    addresses[j],
                    mode="driving",
                    departure_time=departure_time,
                    traffic_model="best_guess",
                )
                if result and "legs" in result[0] and "duration_in_traffic" in result[0]["legs"][0]:
                    duration_s = result[0]["legs"][0]["duration_in_traffic"]["value"]
                    matrix[i][j] = duration_s // 60
                else:
                    log.warning("no_route", origin=addresses[i], destination=addresses[j])
                    matrix[i][j] = float("inf")
            except Exception as exc:
                raise MapsAPIError(
                    f"directions request failed: {addresses[i]} -> {addresses[j]}"
                ) from exc

    log.info("time_matrix_ready", num_addresses=n)
    return matrix


def generate_google_maps_url(
    path: list[int],
    addresses: list[str],
    gmaps: googlemaps.Client,
) -> str:
    """
    Build a Google Maps URL that shows the optimized route.

    Args:
        path: Ordered list of location indices.
        addresses: List of address strings (indexed by path values).
        gmaps: Initialized Google Maps client.

    Returns:
        A ``https://www.google.com/maps/dir/...`` URL.

    Raises:
        MapsAPIError: If geocoding fails for any address.
    """
    coords: list[tuple[float, float]] = []

    for idx in path:
        try:
            result = gmaps.geocode(addresses[idx])
            if not result:
                raise MapsAPIError(f"geocoding returned no results for: {addresses[idx]}")
            loc = result[0]["geometry"]["location"]
            coords.append((loc["lat"], loc["lng"]))
        except MapsAPIError:
            raise
        except Exception as exc:
            raise MapsAPIError(f"geocoding failed for: {addresses[idx]}") from exc

    url = "https://www.google.com/maps/dir/" + "".join(f"{lat},{lng}/" for lat, lng in coords)
    # Close the loop back to the starting point
    url += f"{coords[0][0]},{coords[0][1]}/"
    return url


def get_geocoded_locations(
    gmaps: googlemaps.Client,
    addresses: list[str],
) -> list[dict[str, float] | None]:
    """
    Geocode a list of addresses to lat/lng dictionaries.

    Args:
        gmaps: Initialized Google Maps client.
        addresses: List of address strings.

    Returns:
        List of ``{"lat": float, "lng": float}`` dicts. Entries that fail
        geocoding are ``None`` (logged as warnings, not raised).
    """
    locations: list[dict[str, float] | None] = []

    for address in addresses:
        try:
            result = gmaps.geocode(address)
            if result:
                loc = result[0]["geometry"]["location"]
                locations.append({"lat": loc["lat"], "lng": loc["lng"]})
            else:
                log.warning("geocode_no_result", address=address)
                locations.append(None)
        except Exception as exc:
            log.warning("geocode_failed", address=address, error=str(exc))
            locations.append(None)

    return locations
