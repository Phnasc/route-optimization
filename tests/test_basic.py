"""
Basic tests for the route optimization package.
"""
import unittest
import numpy as np
from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager
from route_optimization.models.path import Path


class TestGraph(unittest.TestCase):
    """Test the Graph class."""
    
    def setUp(self):
        """Set up a test graph."""
        self.graph = Graph(3)
        self.graph.add_edge(0, 1, 10)
        self.graph.add_edge(1, 2, 20)
        self.graph.add_edge(0, 2, 30)
    
    def test_add_edge(self):
        """Test adding an edge to the graph."""
        self.graph.add_edge(2, 0, 40)
        self.assertEqual(self.graph.get_weight(2, 0), 40)
    
    def test_get_weight(self):
        """Test getting the weight of an edge."""
        self.assertEqual(self.graph.get_weight(0, 1), 10)
        self.assertEqual(self.graph.get_weight(0, 2), 30)
    
    def test_evaporate_pheromones(self):
        """Test evaporating pheromones."""
        # Initial pheromone level is 1.0
        self.assertEqual(self.graph.get_pheromone(0, 1), 1.0)
        
        # Evaporate by 50%
        self.graph.evaporate_pheromones(0.5)
        self.assertEqual(self.graph.get_pheromone(0, 1), 0.5)


class TestLocationManager(unittest.TestCase):
    """Test the LocationManager class."""
    
    def setUp(self):
        """Set up a test location manager."""
        self.addresses = ["Location A", "Location B", "Location C"]
        self.time_windows = [(8.0, 9.0), (9.5, 10.5), (11.0, 12.0)]
        self.location_manager = LocationManager(self.addresses, self.time_windows)
    
    def test_get_address(self):
        """Test getting an address."""
        self.assertEqual(self.location_manager.get_address(0), "Location A")
        self.assertEqual(self.location_manager.get_address(2), "Location C")
    
    def test_get_time_window(self):
        """Test getting a time window."""
        self.assertEqual(self.location_manager.get_time_window(1), (9.5, 10.5))
    
    def test_get_num_locations(self):
        """Test getting the number of locations."""
        self.assertEqual(self.location_manager.get_num_locations(), 3)


class TestPath(unittest.TestCase):
    """Test the Path class."""
    
    def setUp(self):
        """Set up a test path."""
        self.path = Path(0, 8.0)
    
    def test_add_location(self):
        """Test adding a location to the path."""
        self.path.add_location(1, 1.0, 9.5)
        self.assertEqual(self.path.get_path(), [0, 1])
        self.assertEqual(self.path.current_time, 9.5)  # Adjusted to earliest time
        
        # Add another location
        self.path.add_location(2, 2.0, 11.0)
        self.assertEqual(self.path.get_path(), [0, 1, 2])
        self.assertEqual(self.path.current_time, 11.5)  # 9.5 + 2.0
    
    def test_get_total_time(self):
        """Test getting the total time of the path."""
        self.path.add_location(1, 1.0, 9.5)
        self.path.add_location(2, 2.0, 11.0)
        self.assertEqual(self.path.get_total_time(), 3.5)  # 11.5 - 8.0
    
    def test_is_visited(self):
        """Test checking if a location has been visited."""
        self.path.add_location(1, 1.0, 9.5)
        self.assertTrue(self.path.is_visited(0))
        self.assertTrue(self.path.is_visited(1))
        self.assertFalse(self.path.is_visited(2))


if __name__ == "__main__":
    unittest.main()
