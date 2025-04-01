"""
Ant Colony Optimization algorithm for route planning.
"""
import heapq
import numpy as np
from typing import List, Tuple, Optional

from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager
from route_optimization.models.path import Path


class AntColonyOptimizer:
    """
    Implements the Ant Colony Optimization algorithm for route planning.
    """
    def __init__(
        self, 
        location_manager: LocationManager, 
        graph: Graph, 
        num_ants: int = 10, 
        num_iterations: int = 100,
        alpha: float = 1.0, 
        beta: float = 2.0, 
        evaporation_rate: float = 0.5,
        max_delivery_time: float = 15.0,
        penalty_time_window: float = 0.5,
        penalty_travel_time: float = 0.8
    ):
        """
        Initialize the Ant Colony Optimizer.
        
        Args:
            location_manager: Manager for location data
            graph: Graph representing travel times between locations
            num_ants: Number of ants to simulate in each iteration
            num_iterations: Number of iterations to run
            alpha: Pheromone importance factor
            beta: Heuristic importance factor
            evaporation_rate: Rate at which pheromones evaporate
            max_delivery_time: Maximum allowed delivery time between locations
            penalty_time_window: Penalty factor for time window violations
            penalty_travel_time: Penalty factor for travel time violations
        """
        self.location_manager = location_manager
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.max_delivery_time = max_delivery_time
        self.penalty_time_window = penalty_time_window
        self.penalty_travel_time = penalty_travel_time
        
        # Priority queue for paths
        self.paths_queue = []
    
    def calculate_probabilities(
        self, 
        current_location: int, 
        visited: set, 
        current_time: float
    ) -> np.ndarray:
        """
        Calculate the probabilities for moving to the next location.
        
        Args:
            current_location: Current location index
            visited: Set of already visited locations
            current_time: Current time
            
        Returns:
            Array of probabilities for each location
        """
        num_locations = self.location_manager.get_num_locations()
        probabilities = np.zeros(num_locations)
        
        for next_location in range(num_locations):
            if next_location not in visited:
                travel_time = self.graph.get_weight(current_location, next_location)
                arrival_time = current_time + travel_time
                earliest_time, latest_time = self.location_manager.get_time_window(next_location)
                
                # Calculate pheromone and heuristic (ACO mechanism)
                pheromone_level = self.graph.get_pheromone(current_location, next_location) ** self.alpha
                
                if travel_time <= self.max_delivery_time and arrival_time <= latest_time:
                    distance_heuristic = (1 / travel_time) ** self.beta
                    probabilities[next_location] = pheromone_level * distance_heuristic
                else:
                    # Apply penalties for constraint violations
                    penalty = 1.0
                    if travel_time > self.max_delivery_time:
                        penalty *= self.penalty_travel_time
                    if arrival_time > latest_time or arrival_time < earliest_time:
                        penalty *= self.penalty_time_window
                    
                    distance_heuristic = (1 / (travel_time + 1)) ** self.beta
                    probabilities[next_location] = penalty * pheromone_level * distance_heuristic
        
        # Normalize probabilities
        total_prob = np.sum(probabilities)
        if total_prob > 0:
            return probabilities / total_prob
        else:
            return np.ones(num_locations) / num_locations
    
    def simulate_ant(self, start_location: int, start_time: float) -> Path:
        """
        Simulate an ant's journey through the locations.
        
        Args:
            start_location: Starting location index
            start_time: Starting time
            
        Returns:
            Completed path
        """
        path = Path(start_location, start_time)
        num_locations = self.location_manager.get_num_locations()
        
        for _ in range(num_locations - 1):
            current_location = path.current_location
            current_time = path.current_time
            
            # Calculate probabilities for next location
            probabilities = self.calculate_probabilities(
                current_location, path.get_visited(), current_time
            )
            
            # Choose next location based on probabilities
            next_location = np.random.choice(range(num_locations), p=probabilities)
            travel_time = self.graph.get_weight(current_location, next_location)
            earliest_time = self.location_manager.get_earliest_time(next_location)
            
            # Add to path
            path.add_location(next_location, travel_time, earliest_time)
        
        return path
    
    def update_pheromones(self, paths: List[Path]) -> None:
        """
        Update pheromone levels based on the quality of paths.
        
        Args:
            paths: List of paths to use for pheromone updates
        """
        # Evaporate all pheromones
        self.graph.evaporate_pheromones(self.evaporation_rate)
        
        # Deposit new pheromones based on path quality
        for path in paths:
            path_locations = path.get_path()
            path_time = path.get_total_time()
            
            if path_time < float('inf'):
                pheromone_deposit = 1 / path_time
                for i in range(len(path_locations) - 1):
                    u, v = path_locations[i], path_locations[i + 1]
                    current_pheromone = self.graph.get_pheromone(u, v)
                    self.graph.update_pheromone(u, v, current_pheromone + pheromone_deposit)
    
    def run(self) -> Tuple[List[int], float]:
        """
        Run the ACO algorithm and return the best path and time.
        
        Returns:
            Tuple of (best_path, best_time)
        """
        best_path = None
        best_time = float('inf')
        
        for iteration in range(self.num_iterations):
            paths = []
            
            # Generate paths using multiple ants
            for ant in range(self.num_ants):
                start_location = 0  # Starting from the first location
                start_time = self.location_manager.get_earliest_time(start_location)
                path = self.simulate_ant(start_location, start_time)
                paths.append(path)
                
                # Keep track of best path using a min heap
                path_time = path.get_total_time()
                heapq.heappush(self.paths_queue, (path_time, id(path), path))
            
            # Update pheromones based on all paths
            self.update_pheromones(paths)
            
            # Check if we found a better path
            if self.paths_queue and self.paths_queue[0][0] < best_time:
                best_time, _, best_path_obj = self.paths_queue[0]
                best_path = best_path_obj.get_path()
        
        return best_path, best_time
