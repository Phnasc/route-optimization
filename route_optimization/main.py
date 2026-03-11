"""Main entry point and public API for route optimization."""

import time

import numpy as np

from route_optimization.algorithms.aco import AntColonyOptimizer
from route_optimization.core.config import settings
from route_optimization.core.exceptions import ValidationError
from route_optimization.core.logging import configure_logging, get_logger
from route_optimization.models.graph import Graph
from route_optimization.models.location import LocationManager
from route_optimization.utils.maps_api import (
    generate_google_maps_url,
    generate_time_matrix,
    get_geocoded_locations,
    initialize_gmaps,
)
from route_optimization.utils.visualization import (
    create_route_map,
    plot_pheromone_levels,
    plot_time_matrix,
)

log = get_logger(__name__)


def build_graph_from_matrix(time_matrix: np.ndarray) -> Graph:
    """
    Build a fully-connected directed Graph from a travel-time matrix.

    Args:
        time_matrix: Square numpy array of travel times (minutes).

    Returns:
        Graph with one edge per ordered address pair.
    """
    n = time_matrix.shape[0]
    graph = Graph(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                graph.add_edge(i, j, float(time_matrix[i][j]))
    return graph


def run_route_optimization(
    api_key: str,
    addresses: list[str],
    order_confirmation_times: list[float],
    num_ants: int = settings.num_ants,
    num_iterations: int = settings.num_iterations,
    max_delivery_time: float = settings.max_delivery_time,
    alpha: float = settings.alpha,
    beta: float = settings.beta,
    evaporation_rate: float = settings.evaporation_rate,
    time_window_duration: float = 0.25,
    visualize: bool = False,
) -> tuple[list[int], float, str]:
    """
    Run the full route optimization pipeline.

    Steps:
        1. Fetch travel times via the Google Maps Directions API.
        2. Build a weighted graph from the time matrix.
        3. Run ACO to find the best delivery order.
        4. Generate a shareable Google Maps URL.
        5. Optionally save visualizations to disk.

    Args:
        api_key: Google Maps API key.
        addresses: Ordered list of delivery addresses.
        order_confirmation_times: Earliest delivery time (hours) for each address.
        num_ants: Number of ants per ACO iteration.
        num_iterations: Number of ACO iterations.
        max_delivery_time: Maximum travel time allowed between two stops (minutes).
        alpha: Pheromone importance factor.
        beta: Heuristic (inverse travel time) importance factor.
        evaporation_rate: Pheromone evaporation fraction per iteration.
        time_window_duration: Width of each delivery window in hours.
        visualize: If True, save PNG/HTML visualizations to the current directory.

    Returns:
        Tuple of ``(best_path, best_time, google_maps_url)`` where *best_path*
        is an ordered list of address indices and *best_time* is total route
        duration in minutes.

    Raises:
        ValidationError: If inputs are malformed.
        MapsAPIError: If the Maps API call fails.
        NoRouteFoundError: If ACO cannot find a valid route.
    """
    if len(addresses) != len(order_confirmation_times):
        raise ValidationError("addresses and order_confirmation_times must have the same length")

    gmaps = initialize_gmaps(api_key)

    time_windows = [(t, t + time_window_duration) for t in order_confirmation_times]
    departure_time = int(time.time())

    time_matrix = generate_time_matrix(gmaps, addresses, departure_time)
    graph = build_graph_from_matrix(time_matrix)
    location_manager = LocationManager(addresses, time_windows)

    optimizer = AntColonyOptimizer(
        location_manager=location_manager,
        graph=graph,
        num_ants=num_ants,
        num_iterations=num_iterations,
        alpha=alpha,
        beta=beta,
        evaporation_rate=evaporation_rate,
        max_delivery_time=max_delivery_time,
    )
    best_path, best_time = optimizer.run()

    google_maps_url = generate_google_maps_url(best_path, addresses, gmaps)

    if visualize:
        try:
            fig = plot_time_matrix(time_matrix, addresses)
            fig.savefig("time_matrix.png")
            log.info("visualization_saved", file="time_matrix.png")

            fig = plot_pheromone_levels(graph, best_path)
            fig.savefig("pheromone_levels.png")
            log.info("visualization_saved", file="pheromone_levels.png")

            locations = get_geocoded_locations(gmaps, addresses)
            route_map = create_route_map(locations, best_path)
            if route_map:
                route_map.save("route_map.html")
                log.info("visualization_saved", file="route_map.html")
        except Exception as exc:
            log.warning("visualization_failed", error=str(exc))

    return best_path, best_time, google_maps_url


def main() -> None:
    """CLI entry point for demonstration purposes."""
    configure_logging()

    ADDRESSES = [
        "Pr. dos Andradas, 45 - Centro, Santos",
        "Av. Bartholomeu de Gusmão, 192 - Ponta da Praia, Santos",
        "Largo Marquês de Monte Alegre, 1 - Valongo, Santos",
        "Av. Gov. Fernando Costa, 343 - Ponta da Praia, Santos",
        "R. Santa Cecília, 795 - Morro de São Bento, Santos",
        "R. Quinze de Novembro, 95 - Centro, Santos - SP",
        "Av. Senador Pinheiro Machado, 48 - Vila Matias, Santos",
    ]
    ORDER_CONFIRMATION_TIMES = [17.0, 17.5, 18.0, 16.5, 17.25, 16.0, 18.5]

    api_key = settings.google_maps_api_key
    if not api_key:
        log.error("missing_api_key", hint="Set GOOGLE_MAPS_API_KEY in your .env file")
        return

    best_path, best_time, google_maps_url = run_route_optimization(
        api_key=api_key,
        addresses=ADDRESSES,
        order_confirmation_times=ORDER_CONFIRMATION_TIMES,
        num_ants=3,
        num_iterations=100,
        visualize=True,
    )

    log.info("result", best_path=best_path, best_time_minutes=best_time)
    log.info("maps_url", url=google_maps_url)

    for idx, loc_idx in enumerate(best_path):
        suffix = " (Final Stop)" if idx == len(best_path) - 1 else ""
        log.info("route_step", step=idx + 1, address=ADDRESSES[loc_idx], suffix=suffix)


if __name__ == "__main__":
    main()
