import json
import random
import os
from typing import Dict, List, Tuple, Any

def get_type(name: str, node_types: Dict[str, Any]) -> str:
    val = node_types.get(name, "intersection")
    return val.get("type", "intersection") if isinstance(val, dict) else val

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

def get_next_output_filename():
    """Find the next available example_N.txt filename."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    counter = 1
    while True:
        filename = os.path.join(base_dir, f"example_{counter}.txt")
        if not os.path.exists(filename):
            return filename
        counter += 1

def print_matrix(matrix, decimals=None, file=None):
    # Format the entire matrix as a list of lists
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

# ------------------ EXAMPLE USAGE (your "YOUR DATA") ------------------
if __name__ == "__main__":
    table = table = [
        [1, 2], #D
        [0, 2, 3, 11], #1
        [0, 1, 3, 14], #2
        [1, 2, 13], #3
        [10, 11, 12, 13], #4
        [13, 15, 14, 9], #5
        [12, 13, 15, 7], #6
        [12, 6, 8, 16], #7
        [15, 16, 7], #8
        [5], #9
        [11,12,4,21,22], #10
        [1,4,10,23], #11
        [10,4,6,7,24], #12
        [3,4,6,5,14], #13
        [2,13,5], #14
        [5,6,8,19], #15
        [7,8,20], #16
        [20,18], #17
        [19,17], #18
        [15,20,18], #19
        [16,17,19], #20
        [23,10], #21
        [24,10], #22
        [11,21], #23
        [12,22], #24
    ]

    idx2label = {
        0: "D",
        1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8",19: "19", 20: "20", 23: "23", 24: "24",
        9: "BSS1", 10: "BSS2",
        11: "C1", 12: "C2", 13: "C3", 14: "C4", 15: "C5", 16: "C6", 17: "C7", 18: "C8", 21: "C9", 22: "C10"
    }

    node_types = {
        "D": "depot",
        **{str(i): "intersection" for i in range(1, 9)},
        "BSS1": "bss", "BSS2": "bss",
        **{f"C{i}": "customer" for i in range(1, 7)},
    }

    # Build everything; set seed for reproducibility if you want (e.g., seed=123)
    graph, labels, Adj, Distance, TrafficFactor = build_graph_with_matrices(
        table=table,
        idx2label=idx2label,
        node_types=node_types,
        undirected=True,
        distance_range=(3.0, 8.0),
        traffic_range=(0.6, 1.0),
        seed=None
    )

    # Get the next available output filename
    output_filename = get_next_output_filename()
    
    # Write all output to the file
    with open(output_filename, 'w', encoding='utf-8') as f:
        # 1) Input format (nodes + edges)
        f.write("=== INPUT FORMAT (JSON) ===\n")
        f.write(json.dumps(graph, indent=2) + "\n")

        # 2) Matrices (using identical edge values)
        f.write("\n=== ORDER OF NODES ===\n")
        f.write(str(labels) + "\n")

        f.write("\n=== Adjacency (0/1) ===\n")
        print_matrix(Adj, file=f)

        f.write("\n=== Distance (km) ===\n")
        print_matrix(Distance, decimals=2, file=f)  # round to 2 decimal places

        f.write("\n=== TrafficFactor ===\n")
        print_matrix(TrafficFactor, decimals=2, file=f)
    
    # Print confirmation message to console
    print(f"Output saved to: {output_filename}")
