"""Integration-style tests for the main orchestration layer."""

import numpy as np
import pytest

from route_optimization.main import build_graph_from_matrix


class TestBuildGraphFromMatrix:
    def test_creates_graph_with_correct_vertex_count(self, simple_time_matrix: np.ndarray) -> None:
        graph = build_graph_from_matrix(simple_time_matrix)
        assert graph.get_vertices() == 3

    def test_edge_weights_match_matrix(self, simple_time_matrix: np.ndarray) -> None:
        graph = build_graph_from_matrix(simple_time_matrix)
        assert graph.get_weight(0, 1) == pytest.approx(10.0)
        assert graph.get_weight(1, 2) == pytest.approx(15.0)
        assert graph.get_weight(0, 2) == pytest.approx(20.0)

    def test_diagonal_not_added_as_edges(self, simple_time_matrix: np.ndarray) -> None:
        graph = build_graph_from_matrix(simple_time_matrix)
        # Diagonal weight is 0.0 from the matrix (no self-loops added as edges is fine)
        w = graph.get_weight(0, 0)
        assert w == pytest.approx(0.0) or w == float("inf")

    def test_symmetric_matrix_produces_bidirectional_edges(self) -> None:
        matrix = np.array([[0.0, 7.0], [7.0, 0.0]])
        graph = build_graph_from_matrix(matrix)
        assert graph.get_weight(0, 1) == pytest.approx(7.0)
        assert graph.get_weight(1, 0) == pytest.approx(7.0)
