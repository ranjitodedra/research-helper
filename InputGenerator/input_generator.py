"""
InputGenerator Module

Combines functionality from:
1. GA_and_CPLEX_Random_Distance_TF_Generator - generates graph and initial matrices
2. make_cplex_input - transforms matrices by adding row/column
3. ENERGY and Time Matrix Calculator - calculates energy and time matrices

Output:
- GA input in JSON format
- 6 matrices for CPLEX: Adjacency, Distance, TrafficFactor, T, Edrop, Ebox
"""

import json
import random
import os
import math
from typing import Dict, List, Tuple, Any


# ============================================================================
# PHYSICS CONSTANTS (from ENERGY and Time Matrix Calculator)
# ============================================================================
M1 = 1530  # Mass with load (kg)
M2 = 5     # Mass without load (kg)
m = 100    # Additional mass (kg)
f = 0.01   # Friction coefficient
base_speed = 50  # Base speed (km/h)
A = 2.5    # Frontal area (m²)
g = 9.8    # Gravity (m/s²)
alpha_deg = 0.86  # Road angle (degrees)
p = 1.205  # Air density (kg/m³)
c = 0.3    # Drag coefficient

# Pre-calculate trigonometric values
cos_alpha = math.cos(math.radians(alpha_deg))
sin_alpha = math.sin(math.radians(alpha_deg))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_type(name: str, node_types: Dict[str, Any]) -> str:
    """Get node type from node_types dictionary."""
    val = node_types.get(name, "intersection")
    return val.get("type", "intersection") if isinstance(val, dict) else val


def print_matrix(matrix, decimals=None, file=None):
    """Format and print matrix with proper brackets and commas."""
    formatted_rows = []
    for row in matrix:
        if decimals is None:
            formatted_rows.append(row)
        else:
            # Round only floats; keep ints as-is
            out = []
            for x in row:
                if isinstance(x, float):
                    out.append(round(x, decimals))
                else:
                    out.append(x)
            formatted_rows.append(out)
    
    # Print as a single list with commas after each row
    output_lines = ["["]
    for i, row in enumerate(formatted_rows):
        if i < len(formatted_rows) - 1:
            output_lines.append(f" {row},")
        else:
            output_lines.append(f" {row}")
    output_lines.append("]")
    
    output = "\n".join(output_lines)
    if file:
        file.write(output + "\n")
    else:
        print(output)


def get_next_output_filename():
    """Find the next available example_N.txt filename."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    counter = 1
    while True:
        filename = os.path.join(base_dir, f"example_{counter}.txt")
        if not os.path.exists(filename):
            return filename
        counter += 1


# ============================================================================
# STEP 1: BUILD GRAPH AND INITIAL MATRICES
# (from GA_and_CPLEX_Random_Distance_TF_Generator)
# ============================================================================

def build_graph_with_matrices(
    table: List[List[int]],
    idx2label: Dict[int, str],
    node_types: Dict[str, Any],
    undirected: bool = True,
    distance_range: Tuple[float, float] = (3.0, 8.0),
    traffic_range: Tuple[float, float] = (0.6, 1.0),
    seed: int = None
):
    """
    Build:
      - nodes/edges JSON (with distance & traffic_factor per edge)
      - Adj (0/1), Distance, TrafficFactor matrices sharing identical edge values

    If undirected=True, each undirected pair gets ONE random (d, tf),
    used consistently in JSON + matrices (matrices symmetric).
    """
    rng = random.Random(seed)
    n = len(table)

    # Build ordered label list by index; fallback to "node{i}" if idx2label missing
    labels = [idx2label.get(i, f"node{i}") for i in range(n)]
    label2idx = {lbl: i for i, lbl in enumerate(labels)}

    # Nodes block
    nodes = {
        lbl: {"type": get_type(lbl, node_types)}
        for lbl in labels
    }

    # Initialize matrices
    Adj = [[0 for _ in range(n)] for _ in range(n)]
    Distance = [[0.0 for _ in range(n)] for _ in range(n)]
    TrafficFactor = [[0.0 for _ in range(n)] for _ in range(n)]

    # Edge storage
    edges = []
    seen = set()  # for undirected dedup on (min_idx, max_idx)

    for i, nbrs in enumerate(table):
        for j in nbrs:
            if i == j:
                continue  # ignore self-loops unless you explicitly want them

            if undirected:
                a, b = (i, j) if i < j else (j, i)
                if (a, b) in seen:
                    continue
                seen.add((a, b))

                # Generate once per undirected edge
                d = round(rng.uniform(*distance_range), 2)
                tf = round(rng.uniform(*traffic_range), 2)

                # Fill matrices symmetrically
                Adj[a][b] = Adj[b][a] = 1
                Distance[a][b] = Distance[b][a] = d
                TrafficFactor[a][b] = TrafficFactor[b][a] = tf

                # Canonical JSON edge direction: lower index -> "from"
                edges.append({
                    "from": labels[a],
                    "to": labels[b],
                    "distance": d,
                    "traffic_factor": tf
                })
            else:
                # Directed edge: generate per directed arc
                d = round(rng.uniform(*distance_range), 2)
                tf = round(rng.uniform(*traffic_range), 2)
                Adj[i][j] = 1
                Distance[i][j] = d
                TrafficFactor[i][j] = tf

                edges.append({
                    "from": labels[i],
                    "to": labels[j],
                    "distance": d,
                    "traffic_factor": tf
                })

    graph = {"nodes": nodes, "edges": edges}
    return graph, labels, Adj, Distance, TrafficFactor


# ============================================================================
# STEP 2: APPLY CPLEX TRANSFORMATION
# (from make_cplex_input)
# ============================================================================

def apply_special_transformation(matrix):
    """
    Apply special transformation to the matrix:
    1. Add 0 to the end of each row
    2. Change row 0 index 1 and row 1 index 0 to matrix[0][2]
    3. Change the last value in row 3 (index 2) to matrix[0][2]
    4. Add a new row at the end with value matrix[0][2] at index 2
    
    Args:
        matrix: A 2D list (list of lists)
    
    Returns:
        Transformed matrix
    """
    # Step 1: Add 0 to each row
    result = [row + [0 if isinstance(row[0], int) else 0.0] for row in matrix]
    
    # Get the special value from row 1, column 3 (index [0][2])
    special_value = matrix[0][2]
    
    # Step 2: Set row 0 index 1 and row 1 index 0 to special_value
    if len(result) > 1:
        result[0][1] = special_value
        result[1][0] = special_value
    
    # Step 3: Change the last value in row 3 (index 2) to special_value
    if len(result) > 2:
        result[2][-1] = special_value
    
    # Step 4: Add a new row at the end
    # The new row should have the same length as other rows
    # and have special_value at index 2
    new_row_length = len(result[0])
    new_row = [0 if isinstance(result[0][0], int) else 0.0] * new_row_length
    new_row[2] = special_value
    result.append(new_row)
    
    return result


# ============================================================================
# STEP 3: CALCULATE ENERGY AND TIME MATRICES
# (from ENERGY and Time Matrix Calculator)
# ============================================================================

def calculate_energy_time_matrices(D, TF):
    """
    Calculate Travel Time, Energy drop, and Energy box matrices.
    
    Args:
        D: Distance matrix (after transformation)
        TF: Traffic Factor matrix (after transformation)
    
    Returns:
        Tuple of (T, Edrop, Ebox) matrices
    """
    n = len(D)
    T = [[0.0 for _ in range(n)] for _ in range(n)]
    Edrop = [[0.0 for _ in range(n)] for _ in range(n)]
    Ebox = [[0.0 for _ in range(n)] for _ in range(n)]
    
    # Calculate matrices
    for i in range(n):
        for j in range(n):
            if D[i][j] != 0.0:  # Only calculate for existing edges
                d = D[i][j]  # Distance in km
                traffic_factor = TF[i][j]
                v0 = base_speed * traffic_factor  # Actual speed (km/h)
                
                # Travel time (minutes) - convert from hours to minutes
                T[i][j] = round((d / v0) * 60, 2)
                
                # Determine dv_dt based on speed
                if 50 <= v0 <= 80:
                    dv_dt = 0.3
                elif 81 <= v0 <= 120:
                    dv_dt = 2
                else:
                    dv_dt = 0
                
                # Calculate Edrop (energy with load)
                Edrop[i][j] = round((1 / 3600) * (
                    M1 * g * (f * cos_alpha + sin_alpha) + 
                    0.0386 * (p * c * A * v0**2) + 
                    (M1 + m) * dv_dt
                ) * d, 2)
                
                # Calculate Ebox (energy without load)
                Ebox[i][j] = round((1 / 3600) * (
                    M2 * g * (f * cos_alpha + sin_alpha) + 
                    0.0386 * (p * c * A * v0**2) + 
                    (M2 + m) * dv_dt
                ) * d, 2)
    
    return T, Edrop, Ebox


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Graph configuration (same as GA_and_CPLEX_Random_Distance_TF_Generator)
    table = [
        [1, 2],  # Node 0: D (depot)
        [0, 2, 8, 11],  # Node 1: 1 (intersection)
        [0, 1, 4, 9, 11],  # Node 2: 2 (intersection)
        [6, 7, 12],  # Node 3: BSS1 (bss)
        [2, 7, 11, 14, 16],  # Node 4: C1 (customer)
        [10, 13, 17, 18, 21],  # Node 5: C2 (customer)
        [3, 12, 15],  # Node 6: 3 (intersection)
        [3, 4, 14],  # Node 7: 4 (intersection)
        [1, 11, 20],  # Node 8: 5 (intersection)
        [2, 16],  # Node 9: C3 (customer)
        [5, 19, 21],  # Node 10: C4 (customer)
        [1, 2, 4, 8, 20],  # Node 11: BSS2 (bss)
        [3, 6],  # Node 12: C5 (customer)
        [5, 18, 19],  # Node 13: 6 (intersection)
        [4, 7, 16],  # Node 14: BSS3 (bss)
        [6, 17, 21],  # Node 15: C6 (customer)
        [4, 9, 14],  # Node 16: 7 (intersection)
        [5, 15],  # Node 17: 8 (intersection)
        [5, 13, 19, 21],  # Node 18: C7 (customer)
        [10, 13, 18, 20, 21],  # Node 19: C8 (customer)
        [8, 11, 19],  # Node 20: C9 (customer)
        [5, 10, 15, 18, 19],  # Node 21: BSS4 (bss)
    ]

    idx2label = {
        0: "D",
        1: "1",
        2: "2",
        3: "BSS1",
        4: "C1",
        5: "C2",
        6: "3",
        7: "4",
        8: "5",
        9: "C3",
        10: "C4",
        11: "BSS2",
        12: "C5",
        13: "6",
        14: "BSS3",
        15: "C6",
        16: "7",
        17: "8",
        18: "C7",
        19: "C8",
        20: "C9",
        21: "BSS4",
    }

    node_types = {
        "BSS1": "bss",
        "BSS2": "bss",
        "BSS3": "bss",
        "BSS4": "bss",
        "C1": "customer",
        "C2": "customer",
        "C3": "customer",
        "C4": "customer",
        "C5": "customer",
        "C6": "customer",
        "C7": "customer",
        "C8": "customer",
        "C9": "customer",
        "D": "depot",
        "1": "intersection",
        "2": "intersection",
        "3": "intersection",
        "4": "intersection",
        "5": "intersection",
        "6": "intersection",
        "7": "intersection",
        "8": "intersection",
    }

    # STEP 1: Build graph and initial matrices
    print("Generating graph and initial matrices...")
    graph, labels, Adj, Distance, TrafficFactor = build_graph_with_matrices(
        table=table,
        idx2label=idx2label,
        node_types=node_types,
        undirected=True,
        distance_range=(3.0, 8.0),
        traffic_range=(0.6, 1.0),
        seed=None  # Change to a number for reproducibility
    )

    # STEP 1.5: Copy distance and traffic_factor from edge "D to 2" to edge "D to 1"
    print("Copying values from edge D→2 to edge D→1...")
    
    # Find edges "D to 1" and "D to 2" in the graph
    edge_d_to_1 = None
    edge_d_to_2 = None
    
    for edge in graph["edges"]:
        if edge["from"] == "D" and edge["to"] == "1":
            edge_d_to_1 = edge
        elif edge["from"] == "D" and edge["to"] == "2":
            edge_d_to_2 = edge
    
    # If both edges exist, copy values from D→2 to D→1
    if edge_d_to_1 is not None and edge_d_to_2 is not None:
        edge_d_to_1["distance"] = edge_d_to_2["distance"]
        edge_d_to_1["traffic_factor"] = edge_d_to_2["traffic_factor"]
        
        # Also update the matrices to keep them in sync
        # Get indices for nodes D, 1, and 2
        idx_D = labels.index("D")
        idx_1 = labels.index("1")
        idx_2 = labels.index("2")
        
        # Copy distance and traffic factor in matrices (both directions for undirected graph)
        Distance[idx_D][idx_1] = Distance[idx_D][idx_2]
        Distance[idx_1][idx_D] = Distance[idx_2][idx_D]
        TrafficFactor[idx_D][idx_1] = TrafficFactor[idx_D][idx_2]
        TrafficFactor[idx_1][idx_D] = TrafficFactor[idx_2][idx_D]
        
        print(f"  Copied values: distance={edge_d_to_2['distance']}, traffic_factor={edge_d_to_2['traffic_factor']}")
    else:
        print("  Warning: Could not find edges D→1 or D→2")

    # STEP 2: Apply CPLEX transformation to all matrices
    print("Applying CPLEX transformations...")
    Adj_transformed = apply_special_transformation(Adj)
    Distance_transformed = apply_special_transformation(Distance)
    TrafficFactor_transformed = apply_special_transformation(TrafficFactor)

    # STEP 3: Calculate energy and time matrices
    print("Calculating energy and time matrices...")
    T, Edrop, Ebox = calculate_energy_time_matrices(Distance_transformed, TrafficFactor_transformed)

    # STEP 4: Write output to file
    output_filename = get_next_output_filename()
    print(f"Writing output to: {output_filename}")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        # 1) GA Input format (nodes + edges in JSON)
        f.write("=== GA INPUT ===\n")
        f.write(json.dumps(graph, indent=2) + "\n")

        # 2) Order of nodes
        f.write("\n=== ORDER OF NODES ===\n")
        f.write(str(labels) + "\n")

        # 3) All 6 matrices for CPLEX
        f.write("\n=== CPLEX MATRICES ===\n")
        
        f.write("\n--- Adjacency (0/1) ---\n")
        print_matrix(Adj_transformed, file=f)

        f.write("\n--- Distance (km) ---\n")
        print_matrix(Distance_transformed, decimals=2, file=f)

        f.write("\n--- TrafficFactor ---\n")
        print_matrix(TrafficFactor_transformed, decimals=2, file=f)

        f.write("\n--- Travel Time T (minutes) ---\n")
        print_matrix(T, decimals=2, file=f)

        f.write("\n--- Energy Drop (Edrop) - with load ---\n")
        print_matrix(Edrop, decimals=2, file=f)

        f.write("\n--- Energy Box (Ebox) - without load ---\n")
        print_matrix(Ebox, decimals=2, file=f)
    
    print(f"Output saved successfully to: {output_filename}")
    print(f"Generated 6 matrices (all {len(Adj_transformed)}x{len(Adj_transformed[0])} after transformation)")
