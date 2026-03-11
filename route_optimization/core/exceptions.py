"""Custom exceptions for the route optimization package."""


class RouteOptimizationError(Exception):
    """Base exception for all package errors."""


class MapsAPIError(RouteOptimizationError):
    """Raised when a Google Maps API call fails."""


class ValidationError(RouteOptimizationError):
    """Raised when input validation fails."""


class NoRouteFoundError(RouteOptimizationError):
    """Raised when the ACO algorithm cannot find a valid route."""
