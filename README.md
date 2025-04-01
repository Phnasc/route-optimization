# Route Optimization using Ant Colony Optimization

This project implements a delivery route optimization system using Ant Colony Optimization (ACO) combined with Machine Learning principles. It finds optimal routes for deliveries while considering time windows and traffic conditions.

## Features

- Route optimization using Ant Colony Optimization algorithm
- Integration with Google Maps API for real-time traffic data
- Consideration of delivery time windows
- Visualization of routes and optimization results
- Modular design for easy extension and maintenance

## Project Structure

```
route-optimization/             # Root of your GitHub repository
├── LICENSE                     # License file
├── README.md                   # Project documentation
├── setup.py                    # Package installation script
├── requirements.txt            # Dependencies
├── .gitignore                  # Git ignore file
├── examples/                   # Example usage scripts
│   ├── __init__.py
│   └── example_optimization.py
├── tests/                      # Test directory  
│   ├── __init__.py
│   └── test_basic.py
└── route_optimization/         # Your actual package
    ├── __init__.py
    ├── main.py
    ├── algorithms/
    │   ├── __init__.py
    │   └── aco.py
    ├── models/
    │   ├── __init__.py
    │   ├── graph.py
    │   ├── location.py
    │   └── path.py
    └── utils/
        ├── __init__.py
        ├── maps_api.py
        └── visualization.py
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/route-optimization.git
cd route-optimization
```

2. Install the package:
```bash
pip install -e .
```

3. For visualization features:
```bash
pip install -e ".[visualization]"
```

## Usage

1. Set your Google Maps API key in `main.py`

2. Run the main script:
```bash
python -m route_optimization.main
```

3. To use in your own code:
```python
from route_optimization.main import run_route_optimization

# Define your addresses and time windows
addresses = [...]
order_times = [...]

# Run the optimization
best_path, best_time, maps_url = run_route_optimization(
    api_key="YOUR_API_KEY",
    addresses=addresses,
    order_confirmation_times=order_times,
    num_ants=10,
    num_iterations=100
)
```

## Algorithm Details

The Ant Colony Optimization algorithm works by simulating ants finding the shortest path. Key components:

- **Pheromone Trails**: Ants deposit pheromones on good paths
- **Heuristic Information**: Travel time between locations influences path selection
- **Time Windows**: Each delivery has a specific time window
- **Constraints**: Maximum delivery times between locations

## Visualizations

The system can generate:
- Time matrix heatmaps
- Pheromone level visualizations
- Interactive route maps (requires folium)

## Requirements

- Python 3.7 or higher
- NumPy
- Google Maps API key
- Matplotlib (for visualization)
- Folium (optional, for interactive maps)

## Author

Pedro Henrique Nascimento

## License

MIT
