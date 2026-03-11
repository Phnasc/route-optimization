"""Location management for delivery route optimization."""

from route_optimization.core.exceptions import ValidationError


class LocationManager:
    """Manages location addresses and delivery time windows."""

    def __init__(self, addresses: list[str], time_windows: list[tuple[float, float]]) -> None:
        """
        Initialize with a list of addresses and their delivery time windows.

        Args:
            addresses: Ordered list of delivery address strings.
            time_windows: Paired list of (earliest, latest) delivery times (hours).

        Raises:
            ValidationError: If addresses and time_windows lengths differ, or if
                any time window is invalid (earliest >= latest).
        """
        if len(addresses) != len(time_windows):
            raise ValidationError("addresses and time_windows must have the same length")
        if len(addresses) == 0:
            raise ValidationError("at least one address is required")
        for i, (earliest, latest) in enumerate(time_windows):
            if earliest >= latest:
                raise ValidationError(
                    f"invalid time window at index {i}: "
                    f"earliest ({earliest}) must be < latest ({latest})"
                )

        self.addresses = addresses
        self.time_windows = time_windows
        self._metadata: dict[int, dict[str, object]] = {
            i: {
                "address": address,
                "earliest_time": time_windows[i][0],
                "latest_time": time_windows[i][1],
            }
            for i, address in enumerate(addresses)
        }

    def get_address(self, location_id: int) -> str:
        """Return the address string for the given location index."""
        return str(self._metadata[location_id]["address"])

    def get_time_window(self, location_id: int) -> tuple[float, float]:
        """Return the (earliest, latest) delivery time window for a location."""
        return self.time_windows[location_id]

    def get_earliest_time(self, location_id: int) -> float:
        """Return the earliest allowed delivery time for a location."""
        return self.time_windows[location_id][0]

    def get_latest_time(self, location_id: int) -> float:
        """Return the latest allowed delivery time for a location."""
        return self.time_windows[location_id][1]

    def get_num_locations(self) -> int:
        """Return the total number of locations."""
        return len(self.addresses)

    def __str__(self) -> str:
        return f"LocationManager(locations={len(self.addresses)})"
