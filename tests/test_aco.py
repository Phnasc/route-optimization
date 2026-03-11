"""Unit tests for the AntColonyOptimizer."""

import numpy as np
import pytest

from route_optimization.algorithms.aco import AntColonyOptimizer
from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager


def make_optimizer(
    num_locations: int = 3,
    num_ants: int = 5,
    num_iterations: int = 10,
    max_delivery_time: float = 100.0,
) -> AntColonyOptimizer:
    """Return an optimizer with a complete graph and wide time windows."""
    addresses = [f"Stop {i}" for i in range(num_locations)]
    time_windows = [(0.0, 100.0)] * num_locations
    lm = LocationManager(addresses, time_windows)

    graph = Graph(num_locations)
    for i in range(num_locations):
        for j in range(num_locations):
            if i != j:
                graph.add_edge(i, j, float((i + j + 1) * 5))

    return AntColonyOptimizer(
        location_manager=lm,
        graph=graph,
        num_ants=num_ants,
        num_iterations=num_iterations,
        max_delivery_time=max_delivery_time,
    )


class TestCalculateProbabilities:
    def test_visited_locations_have_zero_probability(
        self, simple_graph: Graph, simple_location_manager: LocationManager
    ) -> None:
        opt = AntColonyOptimizer(location_manager=simple_location_manager, graph=simple_graph)
        probs = opt.calculate_probabilities(current_location=0, visited={0, 1}, current_time=8.0)
        assert probs[0] == pytest.approx(0.0)
        assert probs[1] == pytest.approx(0.0)
        assert probs[2] > 0.0

    def test_probabilities_sum_to_one(
        self, simple_graph: Graph, simple_location_manager: LocationManager
    ) -> None:
        opt = AntColonyOptimizer(location_manager=simple_location_manager, graph=simple_graph)
        probs = opt.calculate_probabilities(current_location=0, visited={0}, current_time=8.0)
        assert probs.sum() == pytest.approx(1.0)

    def test_fallback_uniform_when_all_zero(self) -> None:
        # Graph with no edges → all weights are inf → fallback uniform
        lm = LocationManager(["A", "B"], [(0.0, 1.0), (0.0, 1.0)])
        graph = Graph(2)
        # No edges added, pheromone defaults to 0 → probabilities all zero
        opt = AntColonyOptimizer(location_manager=lm, graph=graph)
        probs = opt.calculate_probabilities(current_location=0, visited={0}, current_time=0.0)
        assert probs.sum() == pytest.approx(1.0)


class TestSimulateAnt:
    def test_ant_visits_all_locations(self) -> None:
        opt = make_optimizer(num_locations=4)
        path = opt.simulate_ant(start_location=0, start_time=0.0)
        assert len(path.get_path()) == 4
        assert len(path.get_visited()) == 4

    def test_ant_starts_at_correct_location(self) -> None:
        opt = make_optimizer(num_locations=3)
        path = opt.simulate_ant(start_location=0, start_time=0.0)
        assert path.get_path()[0] == 0

    def test_no_repeated_locations(self) -> None:
        opt = make_optimizer(num_locations=5)
        path = opt.simulate_ant(start_location=0, start_time=0.0)
        visited_list = path.get_path()
        assert len(visited_list) == len(set(visited_list))


class TestUpdatePheromones:
    def test_pheromones_decrease_after_evaporation(
        self, simple_graph: Graph, simple_location_manager: LocationManager
    ) -> None:
        opt = AntColonyOptimizer(
            location_manager=simple_location_manager,
            graph=simple_graph,
            evaporation_rate=0.5,
        )
        initial = simple_graph.get_pheromone(0, 1)
        opt.update_pheromones([])  # no paths → only evaporation
        assert simple_graph.get_pheromone(0, 1) < initial

    def test_pheromones_deposited_on_used_edges(
        self, simple_graph: Graph, simple_location_manager: LocationManager
    ) -> None:
        from route_optimization.models.path import Path

        opt = AntColonyOptimizer(
            location_manager=simple_location_manager,
            graph=simple_graph,
            evaporation_rate=0.0,  # disable evaporation to isolate deposit
        )
        path = Path(0, 0.0)
        path.add_location(1, 10.0, 0.0)
        path.add_location(2, 15.0, 0.0)

        before_01 = simple_graph.get_pheromone(0, 1)
        opt.update_pheromones([path])
        assert simple_graph.get_pheromone(0, 1) > before_01


class TestRun:
    def test_run_returns_valid_path(self) -> None:
        opt = make_optimizer(num_locations=4, num_ants=5, num_iterations=20)
        path, total_time = opt.run()
        assert len(path) == 4
        assert len(set(path)) == 4
        assert path[0] == 0
        assert total_time > 0

    def test_run_with_two_locations(self) -> None:
        opt = make_optimizer(num_locations=2, num_ants=3, num_iterations=5)
        path, total_time = opt.run()
        assert sorted(path) == [0, 1]
        assert total_time >= 0

    def test_run_is_deterministic_with_seed(self) -> None:
        np.random.seed(42)
        opt1 = make_optimizer(num_locations=3, num_ants=5, num_iterations=10)
        path1, time1 = opt1.run()

        np.random.seed(42)
        opt2 = make_optimizer(num_locations=3, num_ants=5, num_iterations=10)
        path2, time2 = opt2.run()

        assert path1 == path2
        assert time1 == pytest.approx(time2)
