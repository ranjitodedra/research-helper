import json
import random
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

def print_matrix(matrix, decimals=None):
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
    print("[")
    for i, row in enumerate(formatted_rows):
        if i < len(formatted_rows) - 1:
            print(f" {row},")
        else:
            print(f" {row}")
    print("]")

# ------------------ EXAMPLE USAGE (your "YOUR DATA") ------------------
if __name__ == "__main__":
    table = [
        [1, 2],            # 0 -> D
        [0, 2, 3, 11],     # 1 -> "1"
        [0, 1, 3, 14],     # 2 -> "2"
        [1, 2, 13],        # 3 -> "3"
        [10, 11, 12, 13],  # 4 -> "4"
        [9, 13, 14, 15],   # 5 -> "5"
        [12, 13, 15, 7],   # 6 -> "6"
        [12, 6, 8, 16],    # 7 -> "7"
        [15, 16, 7],       # 8 -> "8"
        [5],               # 9  -> BSS1
        [11, 12, 4],       # 10 -> BSS2
        [1, 4, 10],        # 11 -> C1
        [10, 4, 6, 7],     # 12 -> C2
        [3, 4, 6, 5, 14],  # 13 -> C3
        [2, 13, 5],        # 14 -> C4
        [5, 6, 8],         # 15 -> C5
        [7, 8],            # 16 -> C6
    ]

    idx2label = {
        0: "D",
        1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8",
        9: "BSS1", 10: "BSS2",
        11: "C1", 12: "C2", 13: "C3", 14: "C4", 15: "C5", 16: "C6",
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

    # 1) Input format (nodes + edges)
    print("=== INPUT FORMAT (JSON) ===")
    print(json.dumps(graph, indent=2))

    # 2) Matrices (using identical edge values)
    print("\n=== ORDER OF NODES ===")
    print(labels)

    print("\n=== Adjacency (0/1) ===")
    print_matrix(Adj)

    print("\n=== Distance (km) ===")
    print_matrix(Distance, decimals=2)  # round to 2 decimal places

    print("\n=== TrafficFactor ===")
    print_matrix(TrafficFactor, decimals=2)
