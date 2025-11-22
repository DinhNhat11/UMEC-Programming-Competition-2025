"""Station location optimization using K-Means clustering"""

import random
import math
from typing import List, Tuple
from data_structures import Emergency, Station

def kmeans_cluster(
    points: List[Tuple[float, float]],
    k: int,
    weights: List[float] = None,
    max_iterations: int = 100
) -> List[Tuple[float, float]]:
    """
    K-Means clustering with weighted points.
    
    Args:
        points: List of (x, y) coordinates
        k: Number of clusters
        weights: Optional weights for each point
        max_iterations: Maximum iterations
    
    Returns:
        List of cluster centroids
    """
    if len(points) == 0:
        return []
    
    if weights is None:
        weights = [1.0] * len(points)
    
    # Initialize centroids randomly
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    centroids = [
        (random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        for _ in range(k)
    ]
    
    for iteration in range(max_iterations):
        # Assign points to nearest centroid
        clusters = [[] for _ in range(k)]
        cluster_weights = [[] for _ in range(k)]
        
        for i, point in enumerate(points):
            distances = [
                math.sqrt((point[0] - c[0])**2 + (point[1] - c[1])**2)
                for c in centroids
            ]
            nearest_cluster = min(range(k), key=lambda i: distances[i])
            clusters[nearest_cluster].append(point)
            cluster_weights[nearest_cluster].append(weights[i])
        
        # Update centroids (weighted average)
        new_centroids = []
        for i in range(k):
            if len(clusters[i]) == 0:
                # Keep old centroid if cluster is empty
                new_centroids.append(centroids[i])
            else:
                total_weight = sum(cluster_weights[i])
                if total_weight > 0:
                    weighted_x = sum(p[0] * w for p, w in zip(clusters[i], cluster_weights[i])) / total_weight
                    weighted_y = sum(p[1] * w for p, w in zip(clusters[i], cluster_weights[i])) / total_weight
                    new_centroids.append((weighted_x, weighted_y))
                else:
                    new_centroids.append(centroids[i])
        
        # Check convergence
        if all(
            math.sqrt((new_centroids[i][0] - centroids[i][0])**2 + 
                     (new_centroids[i][1] - centroids[i][1])**2) < 0.01
            for i in range(k)
        ):
            break
        
        centroids = new_centroids
    
    return centroids

def optimize_stations(
    emergencies: List[Emergency],
    station_types: List[str],
    num_stations_per_type: List[int]
) -> List[Station]:
    """
    Optimize station locations using K-Means clustering.
    
    Args:
        emergencies: List of all emergencies
        station_types: List of station types ['fire', 'police', 'medical']
        num_stations_per_type: Number of stations for each type
    
    Returns:
        List of optimized Station objects
    """
    optimized_stations = []
    station_id_counter = {'fire': 1, 'police': 1, 'medical': 1}
    
    for station_type, num_stations in zip(station_types, num_stations_per_type):
        # Filter emergencies that this station type can respond to
        if station_type == 'fire':
            relevant_emergencies = [e for e in emergencies if e.etype in ['fire', 'medical']]
        elif station_type == 'medical':
            relevant_emergencies = [e for e in emergencies if e.etype in ['medical', 'police']]
        elif station_type == 'police':
            relevant_emergencies = [e for e in emergencies if e.etype == 'police']
        else:
            relevant_emergencies = []
        
        if len(relevant_emergencies) == 0:
            # No relevant emergencies, place stations randomly
            for _ in range(num_stations):
                station_id = f"{station_type[0].upper()}{station_id_counter[station_type]}"
                station_id_counter[station_type] += 1
                optimized_stations.append(Station(
                    station_id=station_id,
                    station_type=station_type,
                    x=random.uniform(0, 200),
                    y=random.uniform(0, 200),
                    num_units=2
                ))
            continue
        
        # Extract points and weights
        # Weight by urgency (inverse of priority_s) - more urgent = higher weight
        points = [(e.x, e.y) for e in relevant_emergencies]
        weights = [1.0 / e.priority_s for e in relevant_emergencies]  # Lower priority_s = higher weight
        
        # Cluster
        centroids = kmeans_cluster(points, num_stations, weights)
        
        # Create stations at centroids
        for centroid in centroids:
            station_id = f"{station_type[0].upper()}{station_id_counter[station_type]}"
            station_id_counter[station_type] += 1
            optimized_stations.append(Station(
                station_id=station_id,
                station_type=station_type,
                x=centroid[0],
                y=centroid[1],
                num_units=2
            ))
    
    return optimized_stations

