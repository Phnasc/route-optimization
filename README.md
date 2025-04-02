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
├── README.md                   # Project documentation
├── setup.py                    # Package installation script
├── requirements.txt            # Dependencies
├── .gitignore                  # Git ignore file
├── examples/                   # Example usage scripts
│   ├── __init__.py
│   └── example_optimization.py # In case you want to test with some other adresses 
├── tests/                      # Test directory  
│   ├── __init__.py
│   └── test_basic.py
└── route_optimization/         
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
4. Output Example
   ![image](https://github.com/user-attachments/assets/93997e5c-ffb4-4083-ac97-c4a81ee3c80d)

Delivery Route:
--------------
1. Pr. dos Andradas, 45 - Centro, Santos
   -> 2. Av. Senador Pinheiro Machado, 48 - Vila Matias, Santos
2. Av. Senador Pinheiro Machado, 48 - Vila Matias, Santos
   -> 3. R. Santa Cecília, 795 - Morro de São Bento, Santos
3. R. Santa Cecília, 795 - Morro de São Bento, Santos
   -> 4. Largo Marquês de Monte Alegre, 1 - Valongo, Santos
4. Largo Marquês de Monte Alegre, 1 - Valongo, Santos
   -> 5. R. Quinze de Novembro, 95 - Centro, Santos - SP
5. R. Quinze de Novembro, 95 - Centro, Santos - SP
   -> 6. Av. Gov. Fernando Costa, 343 - Ponta da Praia, Santos
6. Av. Gov. Fernando Costa, 343 - Ponta da Praia, Santos
   -> 7. Av. Bartholomeu de Gusmão, 192 - Ponta da Praia, Santos
7. Av. Bartholomeu de Gusmão, 192 - Ponta da Praia, Santos (Final Destination)

## Algorithm Details

The Ant Colony Optimization algorithm works by simulating ants finding the shortest path. Key components:

- **Pheromone Trails**: Ants deposit pheromones on good paths
- **Heuristic Information**: Travel time between locations influences path selection
- **Time Windows**: Each delivery has a specific time window
- **Constraints**: Maximum delivery times between locations

  If you would like to learn more about it, please feel free to access the file projec_aco_rev1.pdf 

## Visualizations

The system can generate:
- Time matrix heatmaps
  ![image](https://github.com/user-attachments/assets/d04b192f-432c-4d7c-8626-bb51d7e34f86)
- Pheromone level visualizations
  ![image](https://github.com/user-attachments/assets/038338d6-cc6b-4d6f-89c6-bcff1856f32d)

- Interactive route maps (with Google maps and Folium)
  https://www.google.com/maps/dir/-23.9353825,-46.3328107/-23.9442396,-46.3326986/-23.9346401,-46.3359449/-23.9311721,-46.3329727/-23.9325152,-46.330099/-23.9846278,-46.2975248/-23.9903652,-46.30641480000001/-23.9353825,-46.3328107/
## Requirements

- Python 3.7 or higher
- NumPy
- Google Maps API key
- Matplotlib (for visualization)
- Folium (optional, for interactive maps)

## Author

Pedro Henrique Nascimento

