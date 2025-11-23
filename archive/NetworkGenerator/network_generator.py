"""
Network Generator

Automatically generates random network configurations for research examples.
Creates spatially-distributed nodes with proximity-based edge generation while
enforcing depot connectivity constraints.

Usage:
    from network_generator import generate_network
    
    table, idx2label, node_types = generate_network(
        total_nodes=21,
        num_customers=8,
        num_bss=2,
        seed=42
    )
"""

import random
import math
from typing import Dict, List, Tuple, Set, Optional
from collections import deque
import os

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency
    np = None  # type: ignore

try:
    from sklearn.cluster import KMeans
except ImportError:  # pragma: no cover - optional dependency
    KMeans = None  # type: ignore


def get_next_output_filename():
    """Find the next available network_config_N.txt filename."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    counter = 1
    while True:
        filename = os.path.join(base_dir, f"network_config_{counter}.txt")
        if not os.path.exists(filename):
            return filename
        counter += 1


def _euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two 2D points."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def _generate_node_positions(n_nodes: int, seed: int = None) -> List[Tuple[float, float]]:
    """
    Generate 2D spatial positions for all nodes.
    
    Node 0 (Depot): Fixed at edge (10, 50)
    Node 1 (Intersection-1): Near depot at (25, 50)
    Node 2 (Intersection-2): Near depot at (25, 35)
    Other nodes: Random distribution in 100x100 grid
    
    Args:
        n_nodes: Total number of nodes
        seed: Random seed for reproducibility
    
    Returns:
        List of (x, y) coordinate tuples
    """
    rng = random.Random(seed)
    positions = []
    
    # Fixed positions for depot and key intersections
    positions.append((10.0, 50.0))   # Node 0: Depot
    positions.append((25.0, 50.0))   # Node 1: Intersection-1
    positions.append((25.0, 35.0))   # Node 2: Intersection-2
    
    # Random positions for remaining nodes
    # Avoid clustering too close to depot/intersections
    for i in range(3, n_nodes):
        # Generate position with minimum distance from existing nodes
        attempts = 0
        while attempts < 50:
            x = rng.uniform(15, 95)
            y = rng.uniform(10, 90)
            
            # Check minimum distance from depot and first intersections
            if _euclidean_distance((x, y), positions[0]) > 15:
                positions.append((x, y))
                break
            attempts += 1
        else:
            # Fallback: just place it randomly
            positions.append((rng.uniform(20, 90), rng.uniform(10, 90)))
    
    return positions


def _assign_node_roles(
    positions: List[Tuple[float, float]], 
    num_customers: int, 
    num_bss: int,
    seed: Optional[int] = None
) -> Dict[int, str]:
    """
    Assign roles to nodes based on spatial positions.
    
    Strategy:
    - Node 0: Depot (fixed)
    - Node 1, 2: Intersections (fixed)
    - Customers: Quadrant-quota strategy for spatial coverage
    - BSS: K-Means clustering to align with EVRP-BSS heuristic
    - Remaining: Intersections
    
    Args:
        positions: List of (x, y) coordinates
        num_customers: Number of customer nodes
        num_bss: Number of BSS stations
        seed: Optional random seed for deterministic assignment
    
    Returns:
        Dictionary mapping node index to role
    """
    n_nodes = len(positions)
    roles: Dict[int, str] = {}
    rng = random.Random(seed)
    
    # Fixed roles
    roles[0] = 'depot'
    roles[1] = 'intersection'
    roles[2] = 'intersection'
    
    # Available nodes for role assignment (excluding 0, 1, 2)
    available_nodes = list(range(3, n_nodes))
    
    # Assign customers using quadrant quotas
    customer_nodes = _assign_customers_quadrant_quota(
        positions, available_nodes, num_customers, rng
    )
    for idx in customer_nodes:
        roles[idx] = 'customer'
        if idx in available_nodes:
            available_nodes.remove(idx)
    
    # Assign BSS using K-Means clustering
    bss_nodes = _assign_bss_kmeans(
        positions, available_nodes, num_bss, rng
    )
    for idx in bss_nodes:
        roles[idx] = 'bss'
        if idx in available_nodes:
            available_nodes.remove(idx)
    
    # Remaining nodes are intersections
    for idx in available_nodes:
        roles[idx] = 'intersection'
    
    return roles


def _assign_customers_quadrant_quota(
    positions: List[Tuple[float, float]],
    candidate_nodes: List[int],
    num_customers: int,
    rng: random.Random
) -> List[int]:
    """
    Assign customers by ensuring spatial coverage via quadrant quotas.
    """
    if num_customers <= 0 or not candidate_nodes:
        return []
    
    # Compute bounding box for candidate nodes
    xs = [positions[idx][0] for idx in candidate_nodes]
    ys = [positions[idx][1] for idx in candidate_nodes]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    mid_x = 0.5 * (min_x + max_x)
    mid_y = 0.5 * (min_y + max_y)
    
    quadrants = {
        "q1": [],
        "q2": [],
        "q3": [],
        "q4": []
    }
    
    for idx in candidate_nodes:
        x, y = positions[idx]
        if x <= mid_x and y >= mid_y:
            quadrants["q1"].append(idx)
        elif x > mid_x and y >= mid_y:
            quadrants["q2"].append(idx)
        elif x <= mid_x and y < mid_y:
            quadrants["q3"].append(idx)
        else:
            quadrants["q4"].append(idx)
    
    selected: List[int] = []
    taken = set()
    
    # Coverage pass: ensure at most one per quadrant
    for quadrant_name in ("q1", "q2", "q3", "q4"):
        if len(selected) >= num_customers:
            break
        candidates = [idx for idx in quadrants[quadrant_name] if idx not in taken]
        if candidates:
            chosen = rng.choice(candidates)
            selected.append(chosen)
            taken.add(chosen)
    
    # Fill remaining slots from the pooled candidates
    if len(selected) < num_customers:
        remaining_candidates = [idx for idx in candidate_nodes if idx not in taken]
        if remaining_candidates:
            rng.shuffle(remaining_candidates)
            needed = num_customers - len(selected)
            selected.extend(remaining_candidates[:needed])
    
    return selected


def _assign_bss_kmeans(
    positions: List[Tuple[float, float]],
    candidate_nodes: List[int],
    num_bss: int,
    rng: random.Random
) -> List[int]:
    """
    Assign BSS nodes using K-Means clustering on coordinates.
    Mirrors the EVRP-BSS heuristic approach with deterministic seeding.
    """
    if num_bss <= 0 or not candidate_nodes:
        return []
    
    if np is None or KMeans is None:
        raise ImportError(
            "NumPy and scikit-learn are required for K-Means based BSS assignment."
        )
    
    unique_candidates = list(candidate_nodes)
    
    if len(unique_candidates) <= num_bss:
        rng.shuffle(unique_candidates)
        return unique_candidates[:num_bss]
    
    coords = np.array([positions[idx] for idx in unique_candidates], dtype=float)
    kmeans = KMeans(n_clusters=num_bss, random_state=42, n_init=10)
    kmeans.fit(coords)
    
    assigned: List[int] = []
    assigned_set = set()
    
    for cluster_idx in range(num_bss):
        indices = [
            i for i, label in enumerate(kmeans.labels_) if label == cluster_idx
        ]
        if not indices:
            continue
        
        centroid = tuple(kmeans.cluster_centers_[cluster_idx])
        indices.sort(
            key=lambda i: _euclidean_distance(positions[unique_candidates[i]], centroid)
        )
        
        for candidate_idx in indices:
            node_id = unique_candidates[candidate_idx]
            if node_id in assigned_set:
                continue
            assigned.append(node_id)
            assigned_set.add(node_id)
            break
    
    # Fallback if some clusters could not provide a node
    if len(assigned) < num_bss:
        remaining = [idx for idx in unique_candidates if idx not in assigned_set]
        if remaining:
            rng.shuffle(remaining)
            needed = num_bss - len(assigned)
            assigned.extend(remaining[:needed])
    
    return assigned[:num_bss]


def _check_edge_intersection(
    p1: Tuple[float, float], 
    p2: Tuple[float, float],
    p3: Tuple[float, float], 
    p4: Tuple[float, float]
) -> bool:
    """
    Check if line segment p1-p2 intersects with line segment p3-p4.
    
    Uses cross-product method to detect intersection.
    
    Returns:
        True if segments intersect (excluding endpoints)
    """
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    # Check if segments share an endpoint
    if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4:
        return False
    
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def _would_overlap(
    node_a: int, 
    node_b: int, 
    edges: Dict[int, List[int]], 
    positions: List[Tuple[float, float]]
) -> bool:
    """
    Check if adding edge (node_a, node_b) would create overlaps with existing edges.
    
    Args:
        node_a: First node
        node_b: Second node
        edges: Current edge dictionary
        positions: Node positions
    
    Returns:
        True if edge would overlap with existing edges
    """
    new_edge = (positions[node_a], positions[node_b])
    overlap_count = 0
    
    for node_i, neighbors in edges.items():
        for node_j in neighbors:
            if node_i < node_j:  # Check each edge once
                existing_edge = (positions[node_i], positions[node_j])
                if _check_edge_intersection(new_edge[0], new_edge[1], 
                                           existing_edge[0], existing_edge[1]):
                    overlap_count += 1
                    if overlap_count > 2:  # Allow some overlaps
                        return True
    
    return False


def _generate_edges_proximity(
    positions: List[Tuple[float, float]], 
    roles: Dict[int, str],
    seed: int = None,
    min_degree: int = 2,
    max_degree: int = 5
) -> Dict[int, List[int]]:
    """
    Generate edges using proximity-based approach.
    
    Fixed constraint: Depot (0) connects only to nodes 1 and 2
    
    Args:
        positions: Node positions
        roles: Node role assignments
        seed: Random seed
        min_degree: Minimum edges per node
        max_degree: Maximum edges per node
    
    Returns:
        Dictionary mapping node to list of connected neighbors
    """
    rng = random.Random(seed)
    n_nodes = len(positions)
    edges = {i: [] for i in range(n_nodes)}
    
    # HARD CONSTRAINT: Depot edges (always 1 and 2 only)
    edges[0] = [1, 2]
    edges[1] = [0, 2]
    edges[2] = [0, 1]
    
    # Generate proximity-based edges for all other nodes
    for node_i in range(3, n_nodes):
        # Calculate distances to all other nodes
        distances = []
        for node_j in range(n_nodes):
            if node_j == node_i:
                continue
            dist = _euclidean_distance(positions[node_i], positions[node_j])
            distances.append((dist, node_j))
        
        distances.sort()  # Nearest first
        
        # Try to connect to k nearest neighbors
        target_degree = rng.randint(min_degree, max_degree)
        current_degree = len(edges[node_i])
        
        for dist, node_j in distances:
            if current_degree >= target_degree:
                break
            
            # Check if this edge already exists
            if node_j in edges[node_i]:
                continue
            
            # Check degree constraints
            if len(edges[node_j]) >= max_degree:
                continue
            
            # Special constraint: depot can't have more edges
            if node_j == 0:
                continue
            
            # Check for excessive overlaps
            if not _would_overlap(node_i, node_j, edges, positions):
                # Add bidirectional edge
                edges[node_i].append(node_j)
                edges[node_j].append(node_i)
                current_degree += 1
    
    return edges


def _check_connectivity(edges: Dict[int, List[int]], n_nodes: int) -> bool:
    """
    Check if all nodes are reachable from depot using BFS.
    
    Args:
        edges: Edge dictionary
        n_nodes: Total number of nodes
    
    Returns:
        True if graph is fully connected
    """
    visited = set()
    queue = deque([0])  # Start from depot
    visited.add(0)
    
    while queue:
        node = queue.popleft()
        for neighbor in edges[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return len(visited) == n_nodes


def _fix_disconnected_components(
    edges: Dict[int, List[int]], 
    positions: List[Tuple[float, float]]
) -> Dict[int, List[int]]:
    """
    Add minimum edges to connect disconnected components.
    
    Args:
        edges: Current edge dictionary
        positions: Node positions
    
    Returns:
        Updated edge dictionary with full connectivity
    """
    n_nodes = len(positions)
    
    # Find all components using BFS
    visited = set()
    components = []
    
    for start_node in range(n_nodes):
        if start_node in visited:
            continue
        
        component = set()
        queue = deque([start_node])
        component.add(start_node)
        visited.add(start_node)
        
        while queue:
            node = queue.popleft()
            for neighbor in edges[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        
        components.append(component)
    
    # Connect components by finding nearest pairs
    while len(components) > 1:
        # Find closest pair of nodes from different components
        min_dist = float('inf')
        best_pair = None
        comp_indices = None
        
        for i, comp_i in enumerate(components):
            for j, comp_j in enumerate(components[i+1:], start=i+1):
                for node_a in comp_i:
                    for node_b in comp_j:
                        # Skip depot (it already has fixed connections)
                        if node_a == 0 or node_b == 0:
                            continue
                        
                        dist = _euclidean_distance(positions[node_a], positions[node_b])
                        if dist < min_dist:
                            min_dist = dist
                            best_pair = (node_a, node_b)
                            comp_indices = (i, j)
        
        if best_pair:
            # Add edge between components
            node_a, node_b = best_pair
            edges[node_a].append(node_b)
            edges[node_b].append(node_a)
            
            # Merge components
            i, j = comp_indices
            components[i].update(components[j])
            components.pop(j)
        else:
            break
    
    return edges


def _validate_node_degrees(
    edges: Dict[int, List[int]], 
    positions: List[Tuple[float, float]],
    min_degree: int = 2,
    max_degree: int = 5
) -> Dict[int, List[int]]:
    """
    Ensure all nodes have appropriate number of edges.
    
    Args:
        edges: Edge dictionary
        positions: Node positions
        min_degree: Minimum edges per node
        max_degree: Maximum edges per node
    
    Returns:
        Updated edge dictionary with valid degrees
    """
    n_nodes = len(positions)
    
    # Fix nodes with too few edges
    for node_i in range(n_nodes):
        while len(edges[node_i]) < min_degree:
            # Skip depot (it has exactly 2 edges)
            if node_i == 0:
                break
            
            # Find nearest unconnected node
            min_dist = float('inf')
            best_node = None
            
            for node_j in range(n_nodes):
                if node_j == node_i or node_j in edges[node_i]:
                    continue
                if node_j == 0:  # Can't connect to depot
                    continue
                if len(edges[node_j]) >= max_degree:
                    continue
                
                dist = _euclidean_distance(positions[node_i], positions[node_j])
                if dist < min_dist:
                    min_dist = dist
                    best_node = node_j
            
            if best_node is not None:
                edges[node_i].append(best_node)
                edges[node_j].append(node_i)
            else:
                break
    
    # Fix nodes with too many edges (trim longest edges)
    for node_i in range(n_nodes):
        if node_i == 0:  # Don't modify depot
            continue
        
        while len(edges[node_i]) > max_degree:
            # Find longest edge
            max_dist = -1
            farthest_node = None
            
            for node_j in edges[node_i]:
                # Don't remove depot connections for nodes 1 and 2
                if node_i in [1, 2] and node_j == 0:
                    continue
                
                dist = _euclidean_distance(positions[node_i], positions[node_j])
                if dist > max_dist:
                    max_dist = dist
                    farthest_node = node_j
            
            if farthest_node is not None:
                edges[node_i].remove(farthest_node)
                edges[farthest_node].remove(node_i)
            else:
                break
    
    return edges


def _format_output(
    edges: Dict[int, List[int]], 
    roles: Dict[int, str], 
    n_nodes: int
) -> Tuple[List[List[int]], Dict[int, str], Dict[str, str]]:
    """
    Convert internal representation to required output format.
    
    Args:
        edges: Edge dictionary
        roles: Node role assignments
        n_nodes: Total number of nodes
    
    Returns:
        Tuple of (table, idx2label, node_types)
    """
    # Create table (adjacency list)
    table = []
    for i in range(n_nodes):
        neighbors = sorted(edges[i])
        table.append(neighbors)
    
    # Create idx2label mapping
    idx2label = {}
    
    # Depot
    idx2label[0] = "D"
    
    # Intersections (nodes 1, 2, and others)
    intersection_count = 1
    customer_count = 1
    bss_count = 1
    
    for i in range(1, n_nodes):
        role = roles[i]
        
        if role == 'intersection':
            idx2label[i] = str(intersection_count)
            intersection_count += 1
        elif role == 'customer':
            idx2label[i] = f"C{customer_count}"
            customer_count += 1
        elif role == 'bss':
            idx2label[i] = f"BSS{bss_count}"
            bss_count += 1
    
    # Create node_types mapping
    node_types = {}
    for i in range(n_nodes):
        label = idx2label[i]
        node_types[label] = roles[i]
    
    return table, idx2label, node_types


def generate_network(
    total_nodes: int,
    num_customers: int,
    num_bss: int,
    seed: int = None,
    save_to_file: bool = True
) -> Tuple[List[List[int]], Dict[int, str], Dict[str, str]]:
    """
    Generate a random network configuration.
    
    Args:
        total_nodes: Total number of nodes in the network
        num_customers: Number of customer nodes
        num_bss: Number of BSS (battery swap station) nodes
        seed: Random seed for reproducibility (optional)
        save_to_file: Whether to save output to a text file (default: True)
    
    Returns:
        Tuple of (table, idx2label, node_types):
        - table: Adjacency list representation
        - idx2label: Mapping from node index to label
        - node_types: Mapping from label to node type
    
    Raises:
        ValueError: If parameters are invalid
    
    Example:
        >>> table, idx2label, node_types = generate_network(21, 8, 2, seed=42)
        >>> print(table[0])  # Depot connections
        [1, 2]
    """
    # Validate inputs
    if total_nodes < 4:
        raise ValueError("Total nodes must be at least 4 (depot + 2 intersections + 1 other)")
    
    num_depot = 1
    num_fixed_intersections = 2  # Nodes 1 and 2
    num_other = total_nodes - num_depot - num_fixed_intersections
    
    if num_customers + num_bss > num_other:
        raise ValueError(
            f"Cannot fit {num_customers} customers and {num_bss} BSS in {num_other} available nodes"
        )
    
    print(f"Generating network with {total_nodes} nodes...")
    print(f"  - Depot: 1")
    print(f"  - Customers: {num_customers}")
    print(f"  - BSS: {num_bss}")
    print(f"  - Intersections: {total_nodes - num_customers - num_bss - 1}")
    
    # Step 1: Generate spatial positions
    print("Step 1: Generating node positions...")
    positions = _generate_node_positions(total_nodes, seed)
    
    # Step 2: Assign roles
    print("Step 2: Assigning node roles...")
    roles = _assign_node_roles(positions, num_customers, num_bss, seed=seed)
    
    # Step 3: Generate edges with depot constraint
    print("Step 3: Generating edges...")
    edges = _generate_edges_proximity(positions, roles, seed)
    
    # Step 4: Ensure connectivity
    print("Step 4: Checking connectivity...")
    if not _check_connectivity(edges, total_nodes):
        print("  - Graph disconnected, fixing...")
        edges = _fix_disconnected_components(edges, positions)
    
    # Step 5: Validate degrees
    print("Step 5: Validating node degrees...")
    edges = _validate_node_degrees(edges, positions)
    
    # Step 6: Format output
    print("Step 6: Formatting output...")
    table, idx2label, node_types = _format_output(edges, roles, total_nodes)
    
    print("Network generation complete!")
    print(f"  - Depot has {len(table[0])} edges (should be 2): {table[0]}")
    print(f"  - All nodes connected: {_check_connectivity(edges, total_nodes)}")
    
    # Save to file if requested
    if save_to_file:
        output_filename = get_next_output_filename()
        print(f"\nStep 7: Saving to file...")
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("NETWORK CONFIGURATION\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total Nodes: {total_nodes}\n")
            f.write(f"Customers: {num_customers}\n")
            f.write(f"BSS Stations: {num_bss}\n")
            f.write(f"Intersections: {total_nodes - num_customers - num_bss - 1}\n")
            f.write(f"Depot: 1\n")
            if seed is not None:
                f.write(f"Seed: {seed}\n")
            f.write("\n" + "="*70 + "\n\n")
            
            # Write table
            f.write("table = [\n")
            for i, neighbors in enumerate(table):
                label = idx2label[i]
                node_type = node_types[label]
                f.write(f"    {neighbors},  # Node {i}: {label} ({node_type})\n")
            f.write("]\n\n")
            
            # Write idx2label
            f.write("idx2label = {\n")
            for idx in sorted(idx2label.keys()):
                f.write(f"    {idx}: \"{idx2label[idx]}\",\n")
            f.write("}\n\n")
            
            # Write node_types
            f.write("node_types = {\n")
            for label in sorted(node_types.keys(), key=lambda x: (node_types[x], x)):
                f.write(f"    \"{label}\": \"{node_types[label]}\",\n")
            f.write("}\n")
        
        print(f"Saved to: {output_filename}")
    
    return table, idx2label, node_types


# Example usage
if __name__ == "__main__":
    # Generate a network matching the example
    table, idx2label, node_types = generate_network(
        total_nodes=18,
        num_customers=7,
        num_bss=4,
        seed=42
    )
    
    print("\n" + "="*60)
    print("GENERATED NETWORK")
    print("="*60)
    
    print("\ntable = [")
    for i, neighbors in enumerate(table):
        label = idx2label[i]
        print(f"    {neighbors},  # Node {i} ({label})")
    print("]")
    
    print("\nidx2label =", idx2label)
    print("\nnode_types =", node_types)
