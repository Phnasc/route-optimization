"""
Main entry point for the route optimization application.
"""
import time
import numpy as np
from typing import List, Tuple

from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager
from route_optimization.algorithms.aco import AntColonyOptimizer
from route_optimization.utils.maps_api import (
    initialize_gmaps, 
    generate_time_matrix, 
    generate_google_maps_url,
    get_geocoded_locations
)
from route_optimization.utils.visualization import (
    plot_time_matrix,
    create_route_map,
    plot_pheromone_levels
)


def build_graph_from_matrix(time_matrix: np.ndarray) -> Graph:
    """
    Build a graph from the time matrix.
    
    Args:
        time_matrix: Matrix of travel times
        
    Returns:
        Graph object
    """
    num_locations = time_matrix.shape[0]
    graph = Graph(num_locations)
    
    for i in range(num_locations):
        for j in range(num_locations):
            if i != j:
                graph.add_edge(i, j, time_matrix[i][j])
    
    return graph


def run_route_optimization(
    api_key: str, 
    addresses: List[str], 
    order_confirmation_times: List[float],
    num_ants: int = 10, 
    num_iterations: int = 100,
    max_delivery_time: float = 15.0,
    alpha: float = 1.0,
    beta: float = 2.0,
    evaporation_rate: float = 0.5,
    time_window_duration: float = 0.25,  # Default 15-minute window
    visualize: bool = False
) -> Tuple[List[int], float, str]:
    """
    Main function to run the route optimization algorithm.
    
    Args:
        api_key: Google Maps API key
        addresses: List of delivery addresses
        order_confirmation_times: List of order confirmation times
        num_ants: Number of ants for the algorithm
        num_iterations: Number of iterations to run
        max_delivery_time: Maximum allowed delivery time
        alpha: Pheromone importance factor
        beta: Heuristic importance factor
        evaporation_rate: Pheromone evaporation rate
        time_window_duration: Duration of each delivery window
        visualize: Whether to generate visualizations
    
    Returns:
        Tuple of (best_path, best_time, google_maps_url)
    """
    # Initialize Google Maps client
    gmaps = initialize_gmaps(api_key)
    
    print("Generating time matrix...")
    # Generate time windows for each address
    time_windows = [(time, time + time_window_duration) for time in order_confirmation_times]
    
    # Generate time matrix
    departure_time = int(time.time())
    time_matrix = generate_time_matrix(gmaps, addresses, departure_time)
    
    # Build graph from time matrix
    graph = build_graph_from_matrix(time_matrix)
    
    # Initialize location manager
    location_manager = LocationManager(addresses, time_windows)
    
    print(f"Running Ant Colony Optimization with {num_ants} ants and {num_iterations} iterations...")
    # Initialize and run ACO
    optimizer = AntColonyOptimizer(
        location_manager=location_manager,
        graph=graph,
        num_ants=num_ants,
        num_iterations=num_iterations,
        alpha=alpha,
        beta=beta,
        evaporation_rate=evaporation_rate,
        max_delivery_time=max_delivery_time
    )
    
    best_path, best_time = optimizer.run()
    
    # Generate Google Maps URL for visualization
    google_maps_url = generate_google_maps_url(best_path, addresses, gmaps)
    
    # Visualize results if requested
    if visualize:
        try:
            # Plot time matrix
            fig = plot_time_matrix(time_matrix, addresses)
            fig.savefig('time_matrix.png')
            print("Time matrix visualization saved as time_matrix.png")
            
            # Plot pheromone levels
            fig = plot_pheromone_levels(graph, best_path)
            fig.savefig('pheromone_levels.png')
            print("Pheromone levels visualization saved as pheromone_levels.png")
            
            # Create route map if folium is available
            locations = get_geocoded_locations(gmaps, addresses)
            route_map = create_route_map(locations, best_path)
            if route_map:
                route_map.save('route_map.html')
                print("Interactive route map saved as route_map.html")
        except Exception as e:
            print(f"Error generating visualizations: {e}")
    
    return best_path, best_time, google_maps_url


def main():
    """
    Main function to demonstrate the route optimization.
    """
    # Configuration
    ADDRESSES = [
        'Pr. dos Andradas, 45 - Centro, Santos',
        'Av. Bartholomeu de Gusmão, 192 - Ponta da Praia, Santos',
        'Largo Marquês de Monte Alegre, 1 - Valongo, Santos',
        'Av. Gov. Fernando Costa, 343 - Ponta da Praia, Santos',
        'R. Santa Cecília, 795 - Morro de São Bento, Santos',
        'R. Quinze de Novembro, 95 - Centro, Santos - SP',
        'Av. Senador Pinheiro Machado, 48 - Vila Matias, Santos'
    ]
    ORDER_CONFIRMATION_TIMES = [17, 17.5, 18, 16.5, 17.25, 16, 18.5]
    API_KEY = ''  # Insert your Google Maps API key here
    
    if not API_KEY:
        print("Please set your Google Maps API key in the API_KEY variable")
        return
    
    # Run optimization
    best_path, best_time, google_maps_url = run_route_optimization(
        api_key=API_KEY,
        addresses=ADDRESSES,
        order_confirmation_times=ORDER_CONFIRMATION_TIMES,
        num_ants=3,
        num_iterations=100,
        visualize=True
    )
    
    # Output results
    print("\nOptimization Results:")
    print("--------------------")
    print(f"Best Path: {best_path}")
    print(f"Best Time: {best_time} minutes")
    print(f"Google Maps URL: {google_maps_url}")
    
    # Print the route details
    print("\nDelivery Route:")
    print("--------------")
    for idx, location_idx in enumerate(best_path):
        address = ADDRESSES[location_idx]
        if idx < len(best_path) - 1:
            next_location_idx = best_path[idx + 1]
            # Print location and travel time to next location
            print(f"{idx+1}. {address}")
            print(f"   -> {idx+2}. {ADDRESSES[next_location_idx]}")
        else:
            print(f"{idx+1}. {address} (Final Destination)")


if __name__ == '__main__':
    main()
