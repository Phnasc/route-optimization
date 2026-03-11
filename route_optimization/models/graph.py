"""Graph data structure for representing locations and travel times."""


class Graph:
    """Weighted directed graph with pheromone tracking for ACO."""

    def __init__(self, num_vertices: int) -> None:
        """
        Initialize a graph with the given number of vertices.

        Args:
            num_vertices: Number of vertices (locations) in the graph.
        """
        self.V = num_vertices
        self.edges: dict[int, dict[int, float]] = {}
        self.pheromones: dict[int, dict[int, float]] = {}

    def add_edge(self, u: int, v: int, weight: float) -> None:
        """
        Add a directed edge with weight and initialize its pheromone level.

        Args:
            u: Source vertex.
            v: Destination vertex.
            weight: Edge weight (travel time in minutes).
        """
        if u not in self.edges:
            self.edges[u] = {}
            self.pheromones[u] = {}
        self.edges[u][v] = weight
        self.pheromones[u][v] = 1.0  # Initial pheromone level

    def get_weight(self, u: int, v: int) -> float:
        """
        Get the travel time between two vertices.

        Returns infinity if no edge exists.
        """
        return self.edges.get(u, {}).get(v, float("inf"))

    def get_pheromone(self, u: int, v: int) -> float:
        """
        Get the pheromone level between two vertices.

        Returns 0.0 if no edge exists.
        """
        return self.pheromones.get(u, {}).get(v, 0.0)

    def update_pheromone(self, u: int, v: int, value: float) -> None:
        """Set the pheromone level for an existing edge."""
        if u in self.pheromones and v in self.pheromones[u]:
            self.pheromones[u][v] = value

    def evaporate_pheromones(self, rate: float) -> None:
        """
        Multiply all pheromone levels by (1 - rate).

        Args:
            rate: Evaporation rate in the range (0, 1).
        """
        for u in self.pheromones:
            for v in self.pheromones[u]:
                self.pheromones[u][v] *= 1 - rate

    def get_vertices(self) -> int:
        """Return the number of vertices in the graph."""
        return self.V

    def __str__(self) -> str:
        edge_count = sum(len(e) for e in self.edges.values())
        return f"Graph(vertices={self.V}, edges={edge_count})"
