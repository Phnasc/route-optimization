"""
Location management for delivery route optimization.
"""
from typing import Dict, List, Tuple, Any


class LocationManager:
    """
    Manages location data and time windows for deliveries.
    """
    def __init__(self, addresses: List[str], time_windows: List[Tuple[float, float]]):
        """
        Initialize the location manager with addresses and time windows.
        
        Args:
            addresses: List of address strings
            time_windows: List of (earliest_time, latest_time) tuples
        """
        if len(addresses) != len(time_windows):
            raise ValueError("Addresses and time windows must have the same length")
            
        self.addresses = addresses
        self.time_windows = time_windows
        self.metadata = {}
        
        # Initialize location metadata
        for i, address in enumerate(addresses):
            self.metadata[i] = {
                'address': address,
                'time_window': time_windows[i],
                'earliest_time': time_windows[i][0],
                'latest_time': time_windows[i][1]
            }
    
    def get_address(self, location_id: int) -> str:
        """
        Get the address for a specific location.
        
        Args:
            location_id: Index of the location
            
        Returns:
            Address string
        """
        return self.metadata[location_id]['address']
    
    def get_time_window(self, location_id: int) -> Tuple[float, float]:
        """
        Get the time window for a specific location.
        
        Args:
            location_id: Index of the location
            
        Returns:
            Tuple of (earliest_time, latest_time)
        """
        return self.metadata[location_id]['time_window']
    
    def get_earliest_time(self, location_id: int) -> float:
        """
        Get the earliest delivery time for a location.
        
        Args:
            location_id: Index of the location
            
        Returns:
            Earliest time for delivery
        """
        return self.metadata[location_id]['earliest_time']
    
    def get_latest_time(self, location_id: int) -> float:
        """
        Get the latest delivery time for a location.
        
        Args:
            location_id: Index of the location
            
        Returns:
            Latest time for delivery
        """
        return self.metadata[location_id]['latest_time']
    
    def get_num_locations(self) -> int:
        """
        Get the total number of locations.
        
        Returns:
            Number of locations
        """
        return len(self.addresses)
    
    def __str__(self) -> str:
        """String representation of the location manager."""
        return f"LocationManager with {len(self.addresses)} locations"
