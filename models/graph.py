"""
Graph data structure for representing locations and travel times.
"""
from typing import Dict, Optional


class Graph:
    """
    Graph representation of the locations and their travel times.
    """
    def __init__(self, num_vertices: int):
        """
        Initialize a graph with a specified number of vertices.
        
        Args:
            num_vertices: Number of vertices (locations) in the graph
        """
        self.V = num_vertices
        self.edges = {}  # Dictionary of dictionaries for adjacency list
        self.pheromones = {}  # Dictionary for pheromone levels
        
    def add_edge(self, u: int, v: int, weight: float) -> None:
        """
        Add an edge with weight to the graph.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (travel time)
        """
        if u not in self.edges:
            self.edges[u] = {}
            self.pheromones[u] = {}
        self.edges[u][v] = weight
        self.pheromones[u][v] = 1.0  # Initial pheromone level
        
    def get_weight(self, u: int, v: int) -> float:
        """
        Get the weight (travel time) between two vertices.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            The travel time between vertices, or infinity if no edge exists
        """
        return self.edges.get(u, {}).get(v, float('inf'))
    
    def get_pheromone(self, u: int, v: int) -> float:
        """
        Get the pheromone level between two vertices.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            The pheromone level between vertices, or 0 if no edge exists
        """
        return self.pheromones.get(u, {}).get(v, 0.0)
    
    def update_pheromone(self, u: int, v: int, value: float) -> None:
        """
        Update the pheromone level between two vertices.
        
        Args:
            u: Source vertex
            v: Destination vertex
            value: New pheromone value
        """
        if u in self.pheromones and v in self.pheromones[u]:
            self.pheromones[u][v] = value
    
    def evaporate_pheromones(self, rate: float) -> None:
        """
        Evaporate pheromones across all edges by the given rate.
        
        Args:
            rate: Evaporation rate (0 to 1)
        """
        for u in self.pheromones:
            for v in self.pheromones[u]:
                self.pheromones[u][v] *= (1 - rate)
    
    def get_vertices(self) -> int:
        """
        Get the number of vertices in the graph.
        
        Returns:
            Number of vertices
        """
        return self.V
    
    def __str__(self) -> str:
        """String representation of the graph."""
        return f"Graph with {self.V} vertices and {sum(len(edges) for edges in self.edges.values())} edges."
