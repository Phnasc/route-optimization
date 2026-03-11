"""Ant Colony Optimization algorithm for delivery route planning."""

import heapq

import numpy as np

from route_optimization.core.exceptions import NoRouteFoundError
from route_optimization.core.logging import get_logger
from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager
from route_optimization.models.path import Path

log = get_logger(__name__)


class AntColonyOptimizer:
    """
    Ant Colony Optimization (ACO) for the Vehicle Routing Problem with Time Windows.

    Ants probabilistically build routes using pheromone trails and a heuristic
    based on inverse travel time. After each iteration, pheromones evaporate and
    are reinforced along shorter routes.
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
        penalty_travel_time: float = 0.8,
    ) -> None:
        """
        Args:
            location_manager: Manages delivery addresses and time windows.
            graph: Weighted directed graph of travel times.
            num_ants: Number of ants simulated per iteration.
            num_iterations: Total number of ACO iterations.
            alpha: Pheromone trail importance (higher = exploit known routes).
            beta: Heuristic importance (higher = prefer shorter edges).
            evaporation_rate: Fraction of pheromone that evaporates each iteration.
            max_delivery_time: Maximum travel time allowed between stops (minutes).
            penalty_time_window: Penalty multiplier for time-window violations.
            penalty_travel_time: Penalty multiplier for max-delivery-time violations.
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
        self._paths_heap: list[tuple[float, int, Path]] = []

    def calculate_probabilities(
        self,
        current_location: int,
        visited: set[int],
        current_time: float,
    ) -> np.ndarray:
        """
        Compute move probabilities from the current location to all unvisited locations.

        Feasible moves (within max_delivery_time and time window) receive full weight.
        Infeasible moves are penalised but remain selectable to avoid dead ends.

        Returns:
            Normalized probability array of shape (num_locations,).
        """
        num_locations = self.location_manager.get_num_locations()
        probabilities = np.zeros(num_locations)

        for next_loc in range(num_locations):
            if next_loc in visited:
                continue

            travel_time = self.graph.get_weight(current_location, next_loc)
            arrival_time = current_time + travel_time
            _, latest_time = self.location_manager.get_time_window(next_loc)

            pheromone = self.graph.get_pheromone(current_location, next_loc) ** self.alpha

            if travel_time <= self.max_delivery_time and arrival_time <= latest_time:
                heuristic = (1.0 / travel_time) ** self.beta
                probabilities[next_loc] = pheromone * heuristic
            else:
                penalty = 1.0
                if travel_time > self.max_delivery_time:
                    penalty *= self.penalty_travel_time
                if arrival_time > latest_time:
                    penalty *= self.penalty_time_window
                # +1 avoids division by zero for infinite-weight edges
                heuristic = (1.0 / (travel_time + 1)) ** self.beta
                probabilities[next_loc] = penalty * pheromone * heuristic

        total = float(probabilities.sum())
        if total > 0:
            return probabilities / total  # type: ignore[return-value]
        # Fallback: uniform distribution (all paths equally bad)
        return np.ones(num_locations) / num_locations  # type: ignore[return-value]

    def simulate_ant(self, start_location: int, start_time: float) -> Path:
        """
        Simulate a single ant building a complete route from start_location.

        Returns:
            A Path visiting all locations.
        """
        path = Path(start_location, start_time)
        num_locations = self.location_manager.get_num_locations()

        for _ in range(num_locations - 1):
            probabilities = self.calculate_probabilities(
                path.current_location, path.get_visited(), path.current_time
            )
            next_loc = int(np.random.choice(num_locations, p=probabilities))
            travel_time = self.graph.get_weight(path.current_location, next_loc)
            earliest_time = self.location_manager.get_earliest_time(next_loc)
            path.add_location(next_loc, travel_time, earliest_time)

        return path

    def update_pheromones(self, paths: list[Path]) -> None:
        """
        Evaporate pheromones and reinforce edges used in completed paths.

        Better paths (lower total time) deposit more pheromone.
        """
        self.graph.evaporate_pheromones(self.evaporation_rate)

        for path in paths:
            path_time = path.get_total_time()
            if path_time == float("inf") or path_time <= 0:
                continue
            deposit = 1.0 / path_time
            locs = path.get_path()
            for i in range(len(locs) - 1):
                u, v = locs[i], locs[i + 1]
                current = self.graph.get_pheromone(u, v)
                self.graph.update_pheromone(u, v, current + deposit)

    def run(self) -> tuple[list[int], float]:
        """
        Execute the ACO algorithm for num_iterations iterations.

        Returns:
            Tuple of (best_path, best_time) where best_path is an ordered list
            of location indices and best_time is total route duration in minutes.

        Raises:
            NoRouteFoundError: If no valid route is found after all iterations.
        """
        best_path: list[int] | None = None
        best_time = float("inf")

        log.info("aco_start", num_ants=self.num_ants, num_iterations=self.num_iterations)

        for iteration in range(self.num_iterations):
            paths: list[Path] = []

            for _ in range(self.num_ants):
                start = 0
                start_time = self.location_manager.get_earliest_time(start)
                path = self.simulate_ant(start, start_time)
                paths.append(path)
                path_time = path.get_total_time()
                heapq.heappush(self._paths_heap, (path_time, id(path), path))

            self.update_pheromones(paths)

            if self._paths_heap and self._paths_heap[0][0] < best_time:
                best_time, _, best_path_obj = self._paths_heap[0]
                best_path = best_path_obj.get_path()
                best_time = best_path_obj.get_total_time()
                log.debug("new_best", iteration=iteration, best_time=best_time)

        if best_path is None:
            raise NoRouteFoundError("ACO could not find a valid route")

        log.info("aco_complete", best_time=best_time)
        return best_path, best_time
