"""Unit tests for Graph, LocationManager, and Path models."""

import pytest

from route_optimization.core.exceptions import ValidationError
from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager
from route_optimization.models.path import Path


class TestGraph:
    def test_add_edge_and_get_weight(self) -> None:
        g = Graph(3)
        g.add_edge(0, 1, 10.0)
        assert g.get_weight(0, 1) == 10.0

    def test_missing_edge_returns_inf(self) -> None:
        g = Graph(3)
        assert g.get_weight(0, 2) == float("inf")

    def test_initial_pheromone_is_one(self) -> None:
        g = Graph(2)
        g.add_edge(0, 1, 5.0)
        assert g.get_pheromone(0, 1) == 1.0

    def test_missing_pheromone_returns_zero(self) -> None:
        g = Graph(2)
        assert g.get_pheromone(0, 1) == 0.0

    def test_evaporate_pheromones(self) -> None:
        g = Graph(2)
        g.add_edge(0, 1, 5.0)
        g.evaporate_pheromones(0.5)
        assert g.get_pheromone(0, 1) == pytest.approx(0.5)

    def test_evaporate_multiple_times(self) -> None:
        g = Graph(2)
        g.add_edge(0, 1, 5.0)
        g.evaporate_pheromones(0.5)
        g.evaporate_pheromones(0.5)
        assert g.get_pheromone(0, 1) == pytest.approx(0.25)

    def test_update_pheromone(self) -> None:
        g = Graph(2)
        g.add_edge(0, 1, 5.0)
        g.update_pheromone(0, 1, 3.5)
        assert g.get_pheromone(0, 1) == pytest.approx(3.5)

    def test_update_pheromone_on_missing_edge_is_noop(self) -> None:
        g = Graph(2)
        g.update_pheromone(0, 1, 99.0)
        assert g.get_pheromone(0, 1) == 0.0

    def test_get_vertices(self) -> None:
        g = Graph(5)
        assert g.get_vertices() == 5

    def test_str(self) -> None:
        g = Graph(2)
        g.add_edge(0, 1, 1.0)
        assert "vertices=2" in str(g)
        assert "edges=1" in str(g)


class TestLocationManager:
    def test_basic_construction(self) -> None:
        lm = LocationManager(["A", "B"], [(8.0, 9.0), (10.0, 11.0)])
        assert lm.get_num_locations() == 2

    def test_get_address(self) -> None:
        lm = LocationManager(["Depot", "Stop A"], [(8.0, 12.0), (9.0, 13.0)])
        assert lm.get_address(0) == "Depot"
        assert lm.get_address(1) == "Stop A"

    def test_get_time_window(self) -> None:
        lm = LocationManager(["A"], [(9.5, 10.5)])
        assert lm.get_time_window(0) == (9.5, 10.5)

    def test_get_earliest_and_latest_time(self) -> None:
        lm = LocationManager(["A", "B"], [(8.0, 9.0), (11.0, 12.0)])
        assert lm.get_earliest_time(1) == 11.0
        assert lm.get_latest_time(1) == 12.0

    def test_raises_on_mismatched_lengths(self) -> None:
        with pytest.raises(ValidationError, match="same length"):
            LocationManager(["A", "B"], [(8.0, 9.0)])

    def test_raises_on_empty_addresses(self) -> None:
        with pytest.raises(ValidationError, match="at least one"):
            LocationManager([], [])

    def test_raises_on_invalid_time_window(self) -> None:
        with pytest.raises(ValidationError, match="invalid time window"):
            LocationManager(["A"], [(10.0, 9.0)])

    def test_raises_on_equal_time_window_bounds(self) -> None:
        with pytest.raises(ValidationError, match="invalid time window"):
            LocationManager(["A"], [(10.0, 10.0)])


class TestPath:
    def test_initial_state(self) -> None:
        p = Path(0, 8.0)
        assert p.get_path() == [0]
        assert p.current_time == 8.0
        assert p.is_visited(0)

    def test_add_location_after_earliest_time(self) -> None:
        p = Path(0, 8.0)
        p.add_location(1, 1.0, 9.5)  # arrives at 9.0, waits until 9.5
        assert p.current_time == 9.5
        assert p.get_path() == [0, 1]

    def test_add_location_before_earliest_time(self) -> None:
        p = Path(0, 8.0)
        p.add_location(1, 2.0, 8.0)  # arrives at 10.0, no wait needed
        assert p.current_time == 10.0

    def test_get_total_time(self) -> None:
        p = Path(0, 8.0)
        p.add_location(1, 1.0, 9.5)
        p.add_location(2, 2.0, 11.0)
        assert p.get_total_time() == pytest.approx(3.5)  # 11.5 - 8.0

    def test_is_visited(self) -> None:
        p = Path(0, 8.0)
        p.add_location(1, 1.0, 8.0)
        assert p.is_visited(0)
        assert p.is_visited(1)
        assert not p.is_visited(2)

    def test_add_duplicate_location_raises(self) -> None:
        p = Path(0, 8.0)
        p.add_location(1, 1.0, 8.0)
        with pytest.raises(ValueError, match="already in the path"):
            p.add_location(1, 1.0, 8.0)

    def test_get_visited_returns_copy(self) -> None:
        p = Path(0, 8.0)
        visited = p.get_visited()
        visited.add(99)  # mutating the copy must not affect internal state
        assert not p.is_visited(99)

    def test_str(self) -> None:
        p = Path(0, 8.0)
        p.add_location(1, 1.0, 8.0)
        assert "0 -> 1" in str(p)
