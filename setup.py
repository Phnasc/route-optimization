from setuptools import setup, find_packages

setup(
    name="route_optimization",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "googlemaps>=4.4.0",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "visualization": ["folium>=0.12.0"],
    },
    author="Pedro Henrique Nascimento",
    author_email="pedro_nascimento06@hotmail.com",
    description="Route optimization using Ant Colony Optimization",
    keywords="routing, optimization, ant colony, delivery",
    python_requires=">=3.7",
)
