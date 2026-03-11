"""Shared pytest fixtures for the route optimization test suite."""

import numpy as np
import pytest

from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager


@pytest.fixture
def simple_graph() -> Graph:
    """A 3-node fully-connected graph with deterministic weights."""
    g = Graph(3)
    g.add_edge(0, 1, 10.0)
    g.add_edge(1, 0, 10.0)
    g.add_edge(0, 2, 20.0)
    g.add_edge(2, 0, 20.0)
    g.add_edge(1, 2, 15.0)
    g.add_edge(2, 1, 15.0)
    return g


@pytest.fixture
def simple_location_manager() -> LocationManager:
    """A 3-location manager with wide time windows (no constraint violations)."""
    addresses = ["Depot", "Stop A", "Stop B"]
    time_windows = [(8.0, 20.0), (8.0, 20.0), (8.0, 20.0)]
    return LocationManager(addresses, time_windows)


@pytest.fixture
def simple_time_matrix() -> np.ndarray:
    """3×3 symmetric travel-time matrix (minutes)."""
    return np.array(
        [
            [0.0, 10.0, 20.0],
            [10.0, 0.0, 15.0],
            [20.0, 15.0, 0.0],
        ]
    )
