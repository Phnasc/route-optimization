"""Application settings loaded from environment variables or .env file."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_maps_api_key: str = Field(default="", description="Google Maps API key")

    # ACO algorithm defaults
    num_ants: int = Field(default=10, gt=0, description="Number of ants per iteration")
    num_iterations: int = Field(default=100, gt=0, description="Number of ACO iterations")
    alpha: float = Field(default=1.0, gt=0, description="Pheromone importance factor")
    beta: float = Field(default=2.0, gt=0, description="Heuristic importance factor")
    evaporation_rate: float = Field(
        default=0.5, gt=0, lt=1, description="Pheromone evaporation rate"
    )
    max_delivery_time: float = Field(
        default=15.0, gt=0, description="Max allowed travel time between stops (minutes)"
    )


settings = Settings()
