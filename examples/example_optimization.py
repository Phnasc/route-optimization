"""Example usage of the route optimization package."""

import sys

from route_optimization.core.config import settings
from route_optimization.core.logging import configure_logging, get_logger
from route_optimization.main import run_route_optimization

configure_logging()
log = get_logger(__name__)

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


def main() -> None:
    api_key = settings.google_maps_api_key
    if not api_key:
        log.error("missing_api_key", hint="Set GOOGLE_MAPS_API_KEY in your .env file")
        sys.exit(1)

    log.info("example_start", num_stops=len(ADDRESSES))

    best_path, best_time, google_maps_url = run_route_optimization(
        api_key=api_key,
        addresses=ADDRESSES,
        order_confirmation_times=ORDER_CONFIRMATION_TIMES,
        visualize=True,
    )

    log.info("result", best_time_minutes=best_time, maps_url=google_maps_url)

    for idx, loc_idx in enumerate(best_path):
        suffix = " (Final Stop)" if idx == len(best_path) - 1 else ""
        log.info("route_step", step=idx + 1, address=ADDRESSES[loc_idx], suffix=suffix)


if __name__ == "__main__":
    main()
