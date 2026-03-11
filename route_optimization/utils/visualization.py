"""Utilities for visualizing route optimization results."""

from typing import Any

import matplotlib.pyplot as plt
import numpy as np

try:
    import folium

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


def plot_time_matrix(
    time_matrix: np.ndarray,
    labels: list[str] | None = None,
) -> plt.Figure:
    """
    Render a heatmap of the travel-time matrix.

    Args:
        time_matrix: Square matrix of travel times (minutes).
        labels: Optional address labels for the axes.

    Returns:
        Matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(time_matrix, cmap="Blues")

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Travel Time (minutes)", rotation=-90, va="bottom")

    if labels:
        short_labels = [f"{i + 1}: {label.split(',')[0]}" for i, label in enumerate(labels)]
        ax.set_xticks(np.arange(len(short_labels)))
        ax.set_yticks(np.arange(len(short_labels)))
        ax.set_xticklabels(short_labels, rotation=45, ha="right")
        ax.set_yticklabels(short_labels)

    ax.set_title("Travel Time Between Locations (minutes)")

    for i in range(time_matrix.shape[0]):
        for j in range(time_matrix.shape[1]):
            if i != j and time_matrix[i, j] != float("inf"):
                color = "white" if time_matrix[i, j] > 10 else "black"
                ax.text(j, i, f"{time_matrix[i, j]:.0f}", ha="center", va="center", color=color)

    fig.tight_layout()
    return fig


def create_route_map(
    locations: list[dict[str, float] | None],
    path: list[int],
    title: str = "Delivery Route",
) -> Any | None:
    """
    Build an interactive Folium map of the optimized route.

    Args:
        locations: List of ``{"lat": float, "lng": float}`` dicts (None = failed geocode).
        path: Ordered list of location indices.
        title: Map title shown in the HTML.

    Returns:
        A Folium Map object, or None if Folium is not installed or no
        valid coordinates are available.
    """
    if not FOLIUM_AVAILABLE:
        return None

    valid_locs = [loc for loc in locations if loc is not None]
    if not valid_locs:
        return None

    center_lat = sum(loc["lat"] for loc in valid_locs) / len(valid_locs)
    center_lng = sum(loc["lng"] for loc in valid_locs) / len(valid_locs)

    route_map = folium.Map(location=[center_lat, center_lng], zoom_start=13)

    for i, loc in enumerate(locations):
        if loc is None:
            continue
        icon = (
            folium.Icon(color="green", icon="play", prefix="fa")
            if i == path[0]
            else folium.Icon(color="blue", icon="circle", prefix="fa")
        )
        folium.Marker([loc["lat"], loc["lng"]], popup=f"Stop {i + 1}", icon=icon).add_to(route_map)

    path_points = [
        [loc["lat"], loc["lng"]]
        for i in path
        if i < len(locations) and (loc := locations[i]) is not None
    ]
    folium.PolyLine(path_points, color="red", weight=5, opacity=0.7).add_to(route_map)

    title_html = f'<h3 align="center" style="font-size:16px"><b>{title}</b></h3>'
    route_map.get_root().html.add_child(folium.Element(title_html))

    return route_map


def plot_pheromone_levels(
    graph: Any,
    path: list[int],
    figsize: tuple[int, int] = (10, 6),
) -> plt.Figure:
    """
    Visualize pheromone levels across graph edges, highlighting the best path.

    Args:
        graph: Graph object with ``pheromones`` dict and ``V`` vertex count.
        path: Best path to highlight with red rectangles.
        figsize: Matplotlib figure size.

    Returns:
        Matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=figsize)
    n = graph.V
    pheromone_matrix = np.zeros((n, n))

    for u in graph.pheromones:
        for v in graph.pheromones[u]:
            pheromone_matrix[u, v] = graph.pheromones[u][v]

    im = ax.imshow(pheromone_matrix, cmap="viridis")
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Pheromone Level", rotation=-90, va="bottom")

    for i in range(len(path) - 1):
        rect = plt.Rectangle(
            (path[i + 1] - 0.5, path[i] - 0.5), 1, 1, fill=False, edgecolor="red", lw=2
        )
        ax.add_patch(rect)

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_title("Pheromone Levels Between Locations")

    for i in range(n):
        for j in range(n):
            if pheromone_matrix[i, j] > 0:
                color = "white" if pheromone_matrix[i, j] > 0.5 else "black"
                ax.text(
                    j, i, f"{pheromone_matrix[i, j]:.2f}", ha="center", va="center", color=color
                )

    fig.tight_layout()
    return fig
