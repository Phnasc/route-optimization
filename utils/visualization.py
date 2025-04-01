"""
Utilities for visualizing route optimization results.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple

# Try to import optional plotting libraries
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


def plot_time_matrix(time_matrix: np.ndarray, labels: Optional[List[str]] = None) -> plt.Figure:
    """
    Create a heatmap visualization of the time matrix.
    
    Args:
        time_matrix: Time matrix to visualize
        labels: Optional labels for the axes
        
    Returns:
        Matplotlib figure of the heatmap
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    im = ax.imshow(time_matrix, cmap='Blues')
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Travel Time (minutes)", rotation=-90, va="bottom")
    
    # Set labels
    if labels:
        # Create simplified labels for readability
        short_labels = [f"{i+1}: {label.split(',')[0]}" for i, label in enumerate(labels)]
        ax.set_xticks(np.arange(len(short_labels)))
        ax.set_yticks(np.arange(len(short_labels)))
        ax.set_xticklabels(short_labels, rotation=45, ha="right")
        ax.set_yticklabels(short_labels)
    
    # Add title
    ax.set_title("Travel Time Between Locations (minutes)")
    
    # Loop over data dimensions and create text annotations
    for i in range(time_matrix.shape[0]):
        for j in range(time_matrix.shape[1]):
            if i != j:  # Skip diagonal elements
                text = ax.text(j, i, f"{time_matrix[i, j]:.0f}",
                              ha="center", va="center", color="white" if time_matrix[i, j] > 10 else "black")
    
    fig.tight_layout()
    return fig


def create_route_map(locations: List[Dict[str, float]], path: List[int], title: str = "Delivery Route") -> Optional[Any]:
    """
    Create an interactive map of the route if folium is available.
    
    Args:
        locations: List of location dictionaries with lat/lng
        path: List of location indices in order
        title: Title for the map
        
    Returns:
        Folium map object if available, None otherwise
    """
    if not FOLIUM_AVAILABLE:
        print("Folium is not installed. Install it with 'pip install folium' to visualize routes on a map.")
        return None
    
    # Calculate center point of all locations
    lats = [loc['lat'] for loc in locations if loc]
    lngs = [loc['lng'] for loc in locations if loc]
    
    if not lats or not lngs:
        return None
    
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    
    # Create map
    route_map = folium.Map(location=[center_lat, center_lng], zoom_start=13)
    
    # Add markers for each location
    for i, loc in enumerate(locations):
        if loc:
            # Use different color for start/end
            if i == path[0]:
                icon = folium.Icon(color='green', icon='play', prefix='fa')
            else:
                icon = folium.Icon(color='blue', icon='circle', prefix='fa')
                
            folium.Marker(
                [loc['lat'], loc['lng']],
                popup=f"Location {i+1}",
                icon=icon
            ).add_to(route_map)
    
    # Add path lines
    path_points = []
    for i in path:
        if i < len(locations) and locations[i]:
            path_points.append([locations[i]['lat'], locations[i]['lng']])
    
    folium.PolyLine(
        path_points,
        color='red',
        weight=5,
        opacity=0.7
    ).add_to(route_map)
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''
    route_map.get_root().html.add_child(folium.Element(title_html))
    
    return route_map


def plot_pheromone_levels(graph: Any, path: List[int], figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Visualize pheromone levels on the graph edges.
    
    Args:
        graph: Graph object with pheromone data
        path: Best path to highlight
        figsize: Figure size
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Convert pheromone levels to numpy array for visualization
    n = graph.V
    pheromone_matrix = np.zeros((n, n))
    
    for u in graph.pheromones:
        for v in graph.pheromones[u]:
            pheromone_matrix[u, v] = graph.pheromones[u][v]
    
    # Create heatmap
    im = ax.imshow(pheromone_matrix, cmap='viridis')
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Pheromone Level", rotation=-90, va="bottom")
    
    # Highlight the best path
    for i in range(len(path) - 1):
        rect = plt.Rectangle((path[i+1] - 0.5, path[i] - 0.5), 1, 1, fill=False, edgecolor='red', lw=2)
        ax.add_patch(rect)
    
    # Add labels
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_title("Pheromone Levels Between Locations")
    
    # Add text annotations
    for i in range(n):
        for j in range(n):
            if pheromone_matrix[i, j] > 0:
                text = ax.text(j, i, f"{pheromone_matrix[i, j]:.2f}",
                              ha="center", va="center", color="white" if pheromone_matrix[i, j] > 0.5 else "black")
    
    fig.tight_layout()
    return fig
