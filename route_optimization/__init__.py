"""Route Optimization — ACO-based delivery routing with Google Maps integration."""

__version__ = "0.2.0"
__all__ = ["run_route_optimization"]


def __getattr__(name: str) -> object:
    if name == "run_route_optimization":
        from route_optimization.main import run_route_optimization

        return run_route_optimization
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
