"""
Example usage of the route optimization package.
"""
import os
import sys
from route_optimization.main import run_route_optimization

# Sample data
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

def get_api_key():
    """Get Google Maps API key from environment or prompt user."""
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("Google Maps API key not found in environment.")
        api_key = input("Please enter your Google Maps API key: ")
        
    return api_key

def main():
    """Run an example optimization."""
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)
    
    print("Running route optimization example...")
    
    # Run optimization with default parameters
    best_path, best_time, google_maps_url = run_route_optimization(
        api_key=api_key,
        addresses=ADDRESSES,
        order_confirmation_times=ORDER_CONFIRMATION_TIMES,
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
        else:
            print(f"{idx+1}. {address} (Final Destination)")

if __name__ == "__main__":
    main()
