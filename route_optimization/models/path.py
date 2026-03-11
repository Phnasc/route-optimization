"""Path representation for a delivery route."""


class Path:
    """An ordered sequence of locations with arrival timestamps."""

    def __init__(self, starting_location: int, starting_time: float) -> None:
        """
        Initialize a path at the given starting location and time.

        Args:
            starting_location: Index of the first location.
            starting_time: Time of departure from the starting location.
        """
        self.locations: list[int] = [starting_location]
        self.times: list[float] = [starting_time]
        self.visited: set[int] = {starting_location}
        self.current_location = starting_location
        self.current_time = starting_time

    def add_location(self, location: int, travel_time: float, earliest_time: float) -> None:
        """
        Append a location to the path.

        The arrival time is ``current_time + travel_time``, but the effective
        time is clamped to *at least* ``earliest_time`` (wait at the stop if
        we arrive early).

        Args:
            location: Location index to visit next.
            travel_time: Minutes to travel from the current location.
            earliest_time: Earliest allowed service time at the new location.

        Raises:
            ValueError: If the location was already visited.
        """
        if location in self.visited:
            raise ValueError(f"location {location} is already in the path")

        arrival_time = self.current_time + travel_time
        adjusted_time = max(arrival_time, earliest_time)

        self.locations.append(location)
        self.times.append(adjusted_time)
        self.visited.add(location)
        self.current_location = location
        self.current_time = adjusted_time

    def get_total_time(self) -> float:
        """Return total elapsed time from start to last stop."""
        return self.current_time - self.times[0]

    def get_path(self) -> list[int]:
        """Return the ordered list of location indices."""
        return list(self.locations)

    def get_visited(self) -> set[int]:
        """Return the set of visited location indices."""
        return set(self.visited)

    def is_visited(self, location: int) -> bool:
        """Return True if the location has already been visited."""
        return location in self.visited

    def __str__(self) -> str:
        route = " -> ".join(map(str, self.locations))
        return f"Path({route}, total_time={self.get_total_time():.1f})"
