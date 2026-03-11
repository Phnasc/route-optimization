"""Unit tests for Maps API utilities (Google Maps client is fully mocked)."""

from unittest.mock import MagicMock, patch

import pytest

from route_optimization.core.exceptions import MapsAPIError, ValidationError
from route_optimization.utils.maps_api import (
    generate_google_maps_url,
    generate_time_matrix,
    get_geocoded_locations,
    initialize_gmaps,
)


def _directions_response(duration_seconds: int) -> list[dict]:  # type: ignore[type-arg]
    return [{"legs": [{"duration_in_traffic": {"value": duration_seconds}}]}]


def _geocode_response(lat: float, lng: float) -> list[dict]:  # type: ignore[type-arg]
    return [{"geometry": {"location": {"lat": lat, "lng": lng}}}]


class TestInitializeGmaps:
    def test_raises_on_empty_key(self) -> None:
        with pytest.raises(ValidationError, match="GOOGLE_MAPS_API_KEY"):
            initialize_gmaps("")

    def test_creates_client_with_valid_key(self) -> None:
        with patch("route_optimization.utils.maps_api.googlemaps.Client") as mock_cls:
            initialize_gmaps("valid-key")
            mock_cls.assert_called_once_with(key="valid-key")


class TestGenerateTimeMatrix:
    def test_returns_correct_matrix(self) -> None:
        mock_gmaps = MagicMock()
        # 2×2 matrix → 2 off-diagonal calls (0→1, 1→0)
        mock_gmaps.directions.side_effect = [
            _directions_response(600),  # 0→1: 10 min
            _directions_response(1200),  # 1→0: 20 min
        ]
        matrix = generate_time_matrix(mock_gmaps, ["A", "B"], departure_time=0)
        assert matrix[0][0] == 0.0
        assert matrix[0][1] == pytest.approx(10.0)
        assert matrix[1][0] == pytest.approx(20.0)
        assert matrix[1][1] == 0.0

    def test_diagonal_is_zero(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.directions.return_value = _directions_response(300)
        matrix = generate_time_matrix(mock_gmaps, ["A", "B", "C"], departure_time=0)
        assert matrix[0][0] == 0.0
        assert matrix[1][1] == 0.0
        assert matrix[2][2] == 0.0

    def test_missing_route_sets_inf(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.directions.return_value = []  # empty → no route
        matrix = generate_time_matrix(mock_gmaps, ["A", "B"], departure_time=0)
        assert matrix[0][1] == float("inf")

    def test_raises_validation_error_for_single_address(self) -> None:
        mock_gmaps = MagicMock()
        with pytest.raises(ValidationError, match="at least 2"):
            generate_time_matrix(mock_gmaps, ["A"], departure_time=0)

    def test_raises_maps_api_error_on_exception(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.directions.side_effect = RuntimeError("network error")
        with pytest.raises(MapsAPIError, match="directions request failed"):
            generate_time_matrix(mock_gmaps, ["A", "B"], departure_time=0)

    def test_correct_number_of_api_calls(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.directions.return_value = _directions_response(300)
        n = 3
        generate_time_matrix(mock_gmaps, [f"Stop {i}" for i in range(n)], departure_time=0)
        assert mock_gmaps.directions.call_count == n * (n - 1)


class TestGetGeocodedLocations:
    def test_returns_lat_lng_for_valid_addresses(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.side_effect = [
            _geocode_response(10.0, 20.0),
            _geocode_response(30.0, 40.0),
        ]
        result = get_geocoded_locations(mock_gmaps, ["A", "B"])
        assert result[0] == {"lat": 10.0, "lng": 20.0}
        assert result[1] == {"lat": 30.0, "lng": 40.0}

    def test_returns_none_for_failed_geocode(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.return_value = []  # no results
        result = get_geocoded_locations(mock_gmaps, ["Unknown Address"])
        assert result[0] is None

    def test_returns_none_on_api_exception(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.side_effect = RuntimeError("API down")
        result = get_geocoded_locations(mock_gmaps, ["A"])
        assert result[0] is None

    def test_partial_failures(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.side_effect = [
            _geocode_response(1.0, 2.0),
            [],  # fails
            _geocode_response(3.0, 4.0),
        ]
        result = get_geocoded_locations(mock_gmaps, ["A", "Bad", "C"])
        assert result[0] is not None
        assert result[1] is None
        assert result[2] is not None


class TestGenerateGoogleMapsUrl:
    def test_generates_valid_url(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.side_effect = [
            _geocode_response(10.0, 20.0),
            _geocode_response(30.0, 40.0),
        ]
        url = generate_google_maps_url([0, 1], ["A", "B"], mock_gmaps)
        assert url.startswith("https://www.google.com/maps/dir/")
        assert "10.0,20.0" in url
        assert "30.0,40.0" in url

    def test_closes_loop_back_to_start(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.side_effect = [
            _geocode_response(10.0, 20.0),
            _geocode_response(30.0, 40.0),
        ]
        url = generate_google_maps_url([0, 1], ["A", "B"], mock_gmaps)
        # Starting point coordinates appear twice (start + loop-back)
        assert url.count("10.0,20.0") == 2

    def test_raises_maps_api_error_on_geocode_failure(self) -> None:
        mock_gmaps = MagicMock()
        mock_gmaps.geocode.side_effect = RuntimeError("geocode failed")
        with pytest.raises(MapsAPIError, match="geocoding failed"):
            generate_google_maps_url([0, 1], ["A", "B"], mock_gmaps)
