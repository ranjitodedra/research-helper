"""
Unified Input Generator (UIG)
-----------------------------

Combines the maintainRatio, NetworkGenerator, InputGenerator, and
customer&bssLists modules so that users only need to supply the total number of
nodes. The ratio logic determines how many customers and BSS stations are
required, the network is generated using the existing generator, and both the
network configuration and InputGenerator example artifacts (including customer
and station indicator lists) are written to `UIG/`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root (and archived modules) are available for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARCHIVE_ROOT = REPO_ROOT / "archive"
if ARCHIVE_ROOT.exists() and str(ARCHIVE_ROOT) not in sys.path:
    sys.path.insert(0, str(ARCHIVE_ROOT))

from maintainRatio.maintain import compute_counts  # type: ignore
from NetworkGenerator.network_generator import generate_network  # type: ignore
from InputGenerator.input_generator import (  # type: ignore
    build_graph_with_matrices,
    apply_special_transformation,
    calculate_energy_time_matrices,
    print_matrix,
)
from visualization.visualize_graph import visualize_graph  # type: ignore

Table = List[List[int]]
IdxToLabel = Dict[int, str]
NodeTypes = Dict[str, str]


def generate_uig_network(total_nodes: int, seed: Optional[int] = None) -> Dict[str, str]:
    """
    Generate a network using only the total number of nodes.

    Args:
        total_nodes: Total nodes to include in the network.
        seed: Optional seed to forward to the network generator.

    Returns:
        Dictionary containing paths to the network configuration and example files.
    """
    if total_nodes < 4:
        raise ValueError("Total nodes must be at least 4.")

    num_customers, num_bss, _ = compute_counts(total_nodes)

    table, idx2label, node_types = generate_network(
        total_nodes=total_nodes,
        num_customers=num_customers,
        num_bss=num_bss,
        seed=seed,
        save_to_file=False,
    )

    output_path = _resolve_output_path(total_nodes, num_customers, num_bss)
    _write_config_file(
        output_path=output_path,
        total_nodes=total_nodes,
        num_customers=num_customers,
        num_bss=num_bss,
        table=table,
        idx2label=idx2label,
        node_types=node_types,
        seed=seed,
    )

    example_data = _generate_input_generator_payload(
        table=table,
        idx2label=idx2label,
        node_types=node_types,
        seed=seed,
    )
    station_vector, customer_vector = _build_indicator_vectors(idx2label)

    example_path = _resolve_example_path(total_nodes, num_customers, num_bss)
    _write_example_file(
        output_path=example_path,
        example_data=example_data,
        station_vector=station_vector,
        customer_vector=customer_vector,
    )

    visual_path = _resolve_visual_path(total_nodes, num_customers, num_bss)
    _generate_visualization(
        graph=example_data["graph"],
        output_path=visual_path,
    )

    json_path = _resolve_json_path(total_nodes, num_customers, num_bss)
    _write_json_file(
        output_path=json_path,
        graph=example_data["graph"],
    )

    dat_path = _resolve_dat_path(total_nodes, num_customers, num_bss)
    _write_dat_file(
        output_path=dat_path,
        total_nodes=total_nodes,
        station_vector=station_vector,
        customer_vector=customer_vector,
        example_data=example_data,
    )

    print("Artifacts saved:")
    print(f"  - Network configuration: {output_path}")
    print(f"  - Input example:        {example_path}")
    print(f"  - Visualization PNG:    {visual_path}")
    print(f"  - JSON input:           {json_path}")
    print(f"  - DAT input:            {dat_path}")

    return {
        "network_config": output_path,
        "example": example_path,
        "visualization": visual_path,
        "json": json_path,
        "dat": dat_path,
    }


def _resolve_output_path(total_nodes: int, num_customers: int, num_bss: int) -> str:
    """
    Build a unique output filename that reflects the node mix.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    base_name = f"{num_customers}c_{num_bss}bss_{total_nodes}total_network_config"
    extension = ".txt"

    candidate = os.path.join(directory, f"{base_name}{extension}")
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(directory, f"{base_name}_v{version}{extension}")
        if not os.path.exists(candidate):
            return candidate
        version += 1


def _resolve_example_path(total_nodes: int, num_customers: int, num_bss: int) -> str:
    """
    Build a unique output filename for the InputGenerator-style example.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    base_name = f"{num_customers}c_{num_bss}bss_{total_nodes}total_example"
    extension = ".txt"

    candidate = os.path.join(directory, f"{base_name}{extension}")
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(directory, f"{base_name}_v{version}{extension}")
        if not os.path.exists(candidate):
            return candidate
        version += 1


def _resolve_visual_path(total_nodes: int, num_customers: int, num_bss: int) -> str:
    """
    Build a unique output filename for the visualization PNG.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    base_name = f"{num_customers}c_{num_bss}bss_{total_nodes}total"
    extension = ".png"

    candidate = os.path.join(directory, f"{base_name}{extension}")
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(directory, f"{base_name}_v{version}{extension}")
        if not os.path.exists(candidate):
            return candidate
        version += 1


def _resolve_json_path(total_nodes: int, num_customers: int, num_bss: int) -> str:
    """
    Build a unique output filename for the JSON export.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    base_name = f"{num_customers}c_{num_bss}bss_{total_nodes}total"
    extension = ".json"

    candidate = os.path.join(directory, f"{base_name}{extension}")
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(directory, f"{base_name}_v{version}{extension}")
        if not os.path.exists(candidate):
            return candidate
        version += 1


def _resolve_dat_path(total_nodes: int, num_customers: int, num_bss: int) -> str:
    """
    Build a unique output filename for the DAT export.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    base_name = f"{num_customers}c_{num_bss}bss_{total_nodes}total"
    extension = ".dat"

    candidate = os.path.join(directory, f"{base_name}{extension}")
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(directory, f"{base_name}_v{version}{extension}")
        if not os.path.exists(candidate):
            return candidate
        version += 1


def _write_config_file(
    output_path: str,
    total_nodes: int,
    num_customers: int,
    num_bss: int,
    table: Table,
    idx2label: IdxToLabel,
    node_types: NodeTypes,
    seed: Optional[int],
) -> None:
    """
    Persist the network configuration using the same structure as the original
    NetworkGenerator output.
    """
    intersections = total_nodes - num_customers - num_bss - 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("NETWORK CONFIGURATION\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total Nodes: {total_nodes}\n")
        f.write(f"Customers: {num_customers}\n")
        f.write(f"BSS Stations: {num_bss}\n")
        f.write(f"Intersections: {intersections}\n")
        f.write("Depot: 1\n")
        if seed is not None:
            f.write(f"Seed: {seed}\n")
        f.write("\n" + "=" * 70 + "\n\n")

        f.write("table = [\n")
        for i, neighbors in enumerate(table):
            label = idx2label[i]
            node_type = node_types[label]
            f.write(f"    {neighbors},  # Node {i}: {label} ({node_type})\n")
        f.write("]\n\n")

        f.write("idx2label = {\n")
        for idx in sorted(idx2label.keys()):
            f.write(f"    {idx}: \"{idx2label[idx]}\",\n")
        f.write("}\n\n")

        f.write("node_types = {\n")
        for label in sorted(node_types.keys(), key=lambda x: (node_types[x], x)):
            f.write(f"    \"{label}\": \"{node_types[label]}\",\n")
        f.write("}\n")


def _generate_input_generator_payload(
    table: Table,
    idx2label: IdxToLabel,
    node_types: NodeTypes,
    seed: Optional[int],
) -> Dict[str, Any]:
    """
    Reuse InputGenerator helpers to build the matrices, apply transformations,
    and compute energy/time values.
    """
    graph, labels, Adj, Distance, TrafficFactor = build_graph_with_matrices(
        table=table,
        idx2label=idx2label,
        node_types=node_types,
        undirected=True,
        distance_range=(3.0, 8.0),
        traffic_range=(0.6, 1.0),
        seed=seed,
    )

    _copy_depot_edge_values(graph, labels, Distance, TrafficFactor)

    Adj_transformed = apply_special_transformation(Adj)
    Distance_transformed = apply_special_transformation(Distance)
    TrafficFactor_transformed = apply_special_transformation(TrafficFactor)

    T, Edrop, Ebox = calculate_energy_time_matrices(
        Distance_transformed,
        TrafficFactor_transformed,
    )

    return {
        "graph": graph,
        "labels": labels,
        "Adj": Adj_transformed,
        "Distance": Distance_transformed,
        "TrafficFactor": TrafficFactor_transformed,
        "T": T,
        "Edrop": Edrop,
        "Ebox": Ebox,
    }


def _copy_depot_edge_values(
    graph: Dict[str, Any],
    labels: List[str],
    Distance: List[List[float]],
    TrafficFactor: List[List[float]],
) -> None:
    """
    Mirror InputGenerator behavior by copying D→2 distance/traffic_factor into D→1.
    """
    edge_d1 = next(
        (edge for edge in graph["edges"] if edge["from"] == "D" and edge["to"] == "1"),
        None,
    )
    edge_d2 = next(
        (edge for edge in graph["edges"] if edge["from"] == "D" and edge["to"] == "2"),
        None,
    )

    if edge_d1 is None or edge_d2 is None:
        print("Warning: Could not find edges D→1 or D→2; skipping copy step.")
        return

    edge_d1["distance"] = edge_d2["distance"]
    edge_d1["traffic_factor"] = edge_d2["traffic_factor"]

    idx_D = labels.index("D")
    idx_1 = labels.index("1")
    idx_2 = labels.index("2")

    Distance[idx_D][idx_1] = Distance[idx_D][idx_2]
    Distance[idx_1][idx_D] = Distance[idx_2][idx_D]
    TrafficFactor[idx_D][idx_1] = TrafficFactor[idx_D][idx_2]
    TrafficFactor[idx_1][idx_D] = TrafficFactor[idx_2][idx_D]


def _write_example_file(
    output_path: str,
    example_data: Dict[str, Any],
    station_vector: List[int],
    customer_vector: List[int],
) -> None:
    """
    Write the InputGenerator-style example output to disk.
    """
    graph = example_data["graph"]
    labels = example_data["labels"]
    Adj = example_data["Adj"]
    Distance = example_data["Distance"]
    TrafficFactor = example_data["TrafficFactor"]
    T = example_data["T"]
    Edrop = example_data["Edrop"]
    Ebox = example_data["Ebox"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== GA INPUT ===\n")
        f.write(json.dumps(graph, indent=2) + "\n")

        f.write("\n=== ORDER OF NODES ===\n")
        f.write(str(labels) + "\n")

        f.write("\n=== CPLEX MATRICES ===\n")

        f.write(f"\nStation = {station_vector}\n")
        f.write(f"Costumer = {customer_vector}\n")

        f.write("\n--- Adjacency (0/1) ---\n")
        print_matrix(Adj, file=f)

        f.write("\n--- Distance (km) ---\n")
        print_matrix(Distance, decimals=2, file=f)

        f.write("\n--- TrafficFactor ---\n")
        print_matrix(TrafficFactor, decimals=2, file=f)

        f.write("\n--- Travel Time T (minutes) ---\n")
        print_matrix(T, decimals=2, file=f)

        f.write("\n--- Energy Drop (Edrop) - with load ---\n")
        print_matrix(Edrop, decimals=2, file=f)

        f.write("\n--- Energy Box (Ebox) - without load ---\n")
        print_matrix(Ebox, decimals=2, file=f)


def _generate_visualization(
    graph: Dict[str, Any],
    output_path: str,
) -> None:
    """
    Render the network visualization to PNG, logging a warning if dependencies
    are missing instead of crashing.
    """
    try:
        visualize_graph(
            graph,
            output_file=output_path,
            show_labels=True,
            show_edge_labels=False,
            layout="smart_hierarchical",
            node_size=1200,
            spacing_factor=2.5,
        )
    except Exception as exc:  # pragma: no cover - visualization is best-effort
        print(f"Warning: Unable to generate visualization ({exc}).")


def _build_indicator_vectors(idx2label: IdxToLabel) -> Tuple[List[int], List[int]]:
    """
    Reproduce the station/customer indicator vectors used by customer&bssLists.
    """
    size = len(idx2label)
    station_vector = [0] * size
    customer_vector = [0] * size

    for idx in range(size):
        label = idx2label.get(idx, "")
        if label.upper().startswith("BSS"):
            station_vector[idx] = 1
        if label.upper().startswith("C"):
            customer_vector[idx] = 1

    station_vector.append(0)
    customer_vector.append(0)
    return station_vector, customer_vector


def _write_json_file(output_path: str, graph: Dict[str, Any]) -> None:
    """
    Write the JSON payload required by module X using the generated graph.
    """
    payload = {
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "base_speed": 50,
        "modules": [{"capacity": 20, "soc": 100} for _ in range(5)],
        "starting_node": "D",
        "vehicle": {
            "base_mass": 1500,
            "f": 0.01,
            "Cx": 0.3,
            "A": 2.5,
            "m": 100,
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def _write_dat_file(
    output_path: str,
    total_nodes: int,
    station_vector: List[int],
    customer_vector: List[int],
    example_data: Dict[str, Any],
) -> None:
    """
    Emit the DAT file used by module X, reusing matrices from InputGenerator.
    """
    Adj = example_data["Adj"]
    T = example_data["T"]
    Edrop = example_data["Edrop"]
    Ebox = example_data["Ebox"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Initial = 100; // Initial energy level at the depot\n")
        f.write("Eth = 20;\t// Minimum energy level\n")
        f.write("Cswap = 50;\t// Cost of swapping a module\n")
        f.write("Tswap = 2;\t// Time to swap a battery module\n")
        f.write("M = 5;\t\t// The total number of battery modules\n\n")
        f.write("S = 0;\t\t// Sourse of EV\n")
        f.write(f"D = {total_nodes};\t\t// Destination of EV\n")
        f.write("G = 10000;  // Large value\n\n")
        f.write(f"Nodes = {total_nodes};\n")
        f.write("Visits = 13;\n\n")

        f.write(f"Station =  {station_vector};\n")
        f.write(f"Costumer = {customer_vector};\n\n")

        f.write("Adj = \t[\n")
        f.write(_format_matrix_for_dat(Adj))
        f.write("\n];\n\n")

        f.write("Trav =\t[\n")
        f.write(_format_matrix_for_dat(T, decimals=2))
        f.write("\n];\n\n")

        f.write("Edep =\t[\n")
        f.write(_format_matrix_for_dat(Edrop, decimals=2))
        f.write("\n];\n\n")

        f.write("Ebox =\t[\n")
        f.write(_format_matrix_for_dat(Ebox, decimals=2))
        f.write("\n];\n")


def _format_matrix_for_dat(matrix: List[List[Any]], decimals: Optional[int] = None) -> str:
    """
    Format a matrix so that it matches the DAT file style.
    """
    lines = []
    last_row = len(matrix) - 1
    for row_idx, row in enumerate(matrix):
        rendered = []
        for value in row:
            if isinstance(value, float) and decimals is not None:
                rendered.append(f"{value:.{decimals}f}")
            else:
                rendered.append(str(value))
        suffix = "," if row_idx != last_row else ""
        lines.append(f" [{', '.join(rendered)}]{suffix}")
    return "\n".join(lines)


def main() -> None:
    """
    Simple CLI entry point that prompts for the total node count.
    """
    try:
        total_nodes = int(input("Enter total number of nodes: ").strip())
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return

    if total_nodes < 4:
        print("Total nodes must be at least 4.")
        return

    generate_uig_network(total_nodes=total_nodes)


if __name__ == "__main__":
    main()

