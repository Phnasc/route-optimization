"""
Path representation for delivery routes.
"""
from typing import List, Set


class Path:
    """
    Represents a path through locations with timestamps.
    """
    def __init__(self, starting_location: int, starting_time: float):
        """
        Initialize a path with a starting location and time.
        
        Args:
            starting_location: Index of the starting location
            starting_time: Initial time at the starting location
        """
        self.locations = [starting_location]
        self.times = [starting_time]
        self.visited = set([starting_location])
        self.current_location = starting_location
        self.current_time = starting_time
    
    def add_location(self, location: int, travel_time: float, earliest_time: float) -> None:
        """
        Add a location to the path with its arrival time.
        
        Args:
            location: Location index to add
            travel_time: Time to travel from current location
            earliest_time: Earliest allowed time at the new location
        """
        if location in self.visited:
            raise ValueError(f"Location {location} is already in the path")
            
        arrival_time = self.current_time + travel_time
        # Adjust time if arrival is before the location's earliest delivery time
        adjusted_time = max(arrival_time, earliest_time)
        
        self.locations.append(location)
        self.times.append(adjusted_time)
        self.visited.add(location)
        self.current_location = location
        self.current_time = adjusted_time
    
    def get_total_time(self) -> float:
        """
        Get the total time for this path.
        
        Returns:
            Final time in the path
        """
        return self.current_time - self.times[0]
    
    def get_path(self) -> List[int]:
        """
        Get the sequence of locations.
        
        Returns:
            List of location indices in visit order
        """
        return self.locations
    
    def get_visited(self) -> Set[int]:
        """
        Get the set of visited locations.
        
        Returns:
            Set of visited location indices
        """
        return self.visited
    
    def is_visited(self, location: int) -> bool:
        """
        Check if a location has been visited.
        
        Args:
            location: Location index to check
            
        Returns:
            True if the location has been visited
        """
        return location in self.visited
    
    def __str__(self) -> str:
        """String representation of the path."""
        return f"Path: {' -> '.join(map(str, self.locations))}, Total time: {self.get_total_time()}"
