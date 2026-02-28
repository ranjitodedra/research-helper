"""
UIG2 - Unified Input Generator for Project 2
---------------------------------------------

Generates network instances compatible with:
1) EVRP-SCS-and-DWC-Genetic-Algorithm JSON input format
2) CPLEX-Project-2 E_Road.mod DAT format

This module does not modify UIG; it is a separate generator pipeline.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Ensure repository root and archive modules are importable
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARCHIVE_ROOT = REPO_ROOT / "archive"
if ARCHIVE_ROOT.exists() and str(ARCHIVE_ROOT) not in sys.path:
    sys.path.insert(0, str(ARCHIVE_ROOT))

from maintainRatio.maintain import compute_counts  # type: ignore
from NetworkGenerator.network_generator import generate_network  # type: ignore
from InputGenerator.input_generator import (  # type: ignore
    apply_special_transformation,
    build_graph_with_matrices,
    calculate_energy_time_matrices,
)

try:
    from visualization.visualize_graph import visualize_graph  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    visualize_graph = None  # type: ignore

Table = List[List[int]]
IdxToLabel = Dict[int, str]
NodeTypes = Dict[str, str]
MatrixF = List[List[float]]
MatrixI = List[List[int]]


def generate_uig2_network(
    total_nodes: int,
    seed: Optional[int] = None,
    electric_ratio: float = 0.2,
    cs_ratio: Optional[float] = None,
) -> Dict[str, str]:
    """
    Generate UIG2 artifacts for project 2.

    Args:
        total_nodes: Total number of nodes including depot.
        seed: Optional random seed for reproducibility.
        electric_ratio: Ratio of eligible edges to mark as electric in [0, 1].
        cs_ratio: Optional charging-station ratio of total nodes in [0.05, 0.5].
                  If None, uses compute_counts default (0.2).

    Returns:
        Dict of generated output paths.
    """
    if total_nodes < 4:
        raise ValueError("Total nodes must be at least 4.")
    if not (0.0 <= electric_ratio <= 1.0):
        raise ValueError("electric_ratio must be within [0.0, 1.0].")
    
    # Validate cs_ratio if provided
    if cs_ratio is not None:
        if not (0.05 <= cs_ratio <= 0.5):
            raise ValueError("cs_ratio must be within [0.05, 0.5].")
        target_bss = max(1, round(cs_ratio * total_nodes))
    else:
        target_bss = None
    
    # Always generate with baseline counts to keep map fixed
    num_customers, baseline_bss, _ = compute_counts(total_nodes)
    if num_customers <= 0:
        raise ValueError("Generated customer count is zero; increase total_nodes.")
    if baseline_bss <= 0:
        raise ValueError("Generated BSS count is zero; increase total_nodes.")

    # Generate network with baseline counts (fixed map)
    table, idx2label, node_types = _safe_generate_network(
        total_nodes=total_nodes,
        num_customers=num_customers,
        num_bss=baseline_bss,
        seed=seed,
    )

    (
        graph,
        labels,
        adj,
        distance,
        traffic,
    ) = build_graph_with_matrices(
        table=table,
        idx2label=idx2label,
        node_types=node_types,
        undirected=True,
        distance_range=(3.0, 8.0),
        traffic_range=(0.6, 1.0),
        seed=seed,
    )

    _copy_depot_edge_values(graph, labels, distance, traffic)

    # Relabel nodes if cs_ratio override is specified (keeps same map, only changes node types)
    if target_bss is not None and target_bss != baseline_bss:
        idx2label, node_types, labels = _relabel_for_cs_ratio(
            idx2label=idx2label,
            node_types=node_types,
            labels=labels,
            graph=graph,
            target_bss=target_bss,
            baseline_bss=baseline_bss,
            seed=seed,
        )
        # Update num_bss for output file naming
        num_bss = target_bss
    else:
        num_bss = baseline_bss

    # Electric edge selection and matrix preparation on the pre-transform matrix.
    edge_rng = random.Random(seed)
    eligible_pairs = _collect_eligible_edge_pairs(adj, labels)
    electric_pairs = _select_electric_pairs(eligible_pairs, electric_ratio, edge_rng)
    e_road_raw = _build_eroad_matrix(len(labels), electric_pairs, directed=True)

    # For electric roads, force traffic factor to 1.0 so speed is constant.
    _apply_electric_traffic_override(traffic, electric_pairs, value=1.0)

    # Apply CPLEX transformation that expands matrices from NxN to (N+1)x(N+1)
    # (matrices are total_nodes x total_nodes from build_graph_with_matrices)
    adj_t = apply_special_transformation(adj)
    distance_t = apply_special_transformation(distance)
    traffic_t = apply_special_transformation(traffic)
    e_road_t = apply_special_transformation(e_road_raw)

    trav_t, edep_t, ebox_t = calculate_energy_time_matrices(distance_t, traffic_t)

    # Create station/customer vectors with trailing 0 for CPLEX indexing style.
    # Matrices are total_nodes x total_nodes before transformation, (total_nodes+1) x (total_nodes+1) after
    station_vector, customer_vector = _build_indicator_vectors(idx2label, total_nodes)

    # Build GA payload from mapped labels and selected electric edges.
    ga_payload = _build_ga_payload(
        labels=labels,
        node_types=node_types,
        distance=distance,
        traffic=traffic,
        electric_pairs=electric_pairs,
    )

    _validate_ga_payload(ga_payload)

    json_path = _resolve_output_path(total_nodes, num_customers, num_bss, ".json")
    dat_path = _resolve_output_path(total_nodes, num_customers, num_bss, ".dat")
    txt_path = _resolve_output_path(total_nodes, num_customers, num_bss, "_example.txt")
    png_path = _resolve_output_path(total_nodes, num_customers, num_bss, ".png")

    _write_json(json_path, ga_payload)
    _write_dat(
        output_path=dat_path,
        total_nodes=total_nodes,
        station_vector=station_vector,
        customer_vector=customer_vector,
        adj=adj_t,
        dist=distance_t,
        trav=trav_t,
        edep=edep_t,
        ebox=ebox_t,
        eroad=e_road_t,
    )
    # Calculate effective CS ratio for summary
    effective_cs_ratio = num_bss / total_nodes if total_nodes > 0 else 0.0
    
    _write_summary(
        output_path=txt_path,
        total_nodes=total_nodes,
        num_customers=num_customers,
        num_bss=num_bss,
        seed=seed,
        electric_ratio=electric_ratio,
        cs_ratio=effective_cs_ratio,
        ga_payload=ga_payload,
        electric_pairs=electric_pairs,
    )
    _generate_visualization(graph=graph, output_path=png_path)

    return {
        "json": json_path,
        "dat": dat_path,
        "summary": txt_path,
        "visualization": png_path,
    }


def _safe_generate_network(
    total_nodes: int,
    num_customers: int,
    num_bss: int,
    seed: Optional[int],
) -> Tuple[Table, IdxToLabel, NodeTypes]:
    try:
        return generate_network(
            total_nodes=total_nodes,
            num_customers=num_customers,
            num_bss=num_bss,
            seed=seed,
            save_to_file=False,
        )
    except ImportError:
        # Fallback when optional KMeans dependencies are not installed.
        return _generate_network_fallback(total_nodes, num_customers, num_bss, seed)


def _generate_network_fallback(
    total_nodes: int,
    num_customers: int,
    num_bss: int,
    seed: Optional[int],
) -> Tuple[Table, IdxToLabel, NodeTypes]:
    rng = random.Random(seed)

    idx2label: IdxToLabel = {0: "D"}
    node_types: NodeTypes = {"D": "depot"}

    next_idx = 1
    intersection_count = max(2, total_nodes - num_customers - num_bss - 1)
    for i in range(intersection_count):
        label = str(i + 1)
        idx2label[next_idx] = label
        node_types[label] = "intersection"
        next_idx += 1

    for i in range(num_customers):
        label = f"C{i + 1}"
        idx2label[next_idx] = label
        node_types[label] = "customer"
        next_idx += 1

    for i in range(num_bss):
        label = f"BSS{i + 1}"
        idx2label[next_idx] = label
        node_types[label] = "bss"
        next_idx += 1

    # Ensure exact size if rounding/inputs create edge cases.
    while next_idx < total_nodes:
        label = str(intersection_count + 1)
        intersection_count += 1
        idx2label[next_idx] = label
        node_types[label] = "intersection"
        next_idx += 1

    table: Table = [[] for _ in range(total_nodes)]

    def add_edge(a: int, b: int) -> None:
        if b not in table[a]:
            table[a].append(b)
        if a not in table[b]:
            table[b].append(a)

    # Depot connectivity rule.
    add_edge(0, 1)
    add_edge(0, 2)
    add_edge(1, 2)

    # Backbone chain for global connectivity.
    for i in range(2, total_nodes - 1):
        add_edge(i, i + 1)

    # Random extra edges for route diversity, avoiding depot over-connection.
    candidate_pairs: List[Tuple[int, int]] = []
    for i in range(1, total_nodes):
        for j in range(i + 1, total_nodes):
            if i == 0 or j == 0:
                continue
            candidate_pairs.append((i, j))

    rng.shuffle(candidate_pairs)
    extra_edges = max(total_nodes // 2, 1)
    for a, b in candidate_pairs[:extra_edges]:
        add_edge(a, b)

    for i in range(len(table)):
        table[i] = sorted(table[i])

    return table, idx2label, node_types


def _resolve_output_path(
    total_nodes: int,
    num_customers: int,
    num_bss: int,
    suffix: str,
) -> str:
    directory = os.path.dirname(os.path.abspath(__file__))
    base_name = f"{num_customers}c_{num_bss}bss_{total_nodes}total"
    candidate = os.path.join(directory, f"{base_name}{suffix}")
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(directory, f"{base_name}_v{version}{suffix}")
        if not os.path.exists(candidate):
            return candidate
        version += 1


def _relabel_for_cs_ratio(
    idx2label: IdxToLabel,
    node_types: NodeTypes,
    labels: List[str],
    graph: Dict[str, Any],
    target_bss: int,
    baseline_bss: int,
    seed: Optional[int],
) -> Tuple[IdxToLabel, NodeTypes, List[str]]:
    """
    Relabel intersection nodes as BSS (or vice versa) to achieve target CS density
    while keeping the same map topology and distances.
    
    Args:
        idx2label: Mapping from index to node label
        node_types: Mapping from label to node type
        labels: Ordered list of labels by index
        graph: Graph dictionary with nodes and edges
        target_bss: Desired number of BSS nodes
        baseline_bss: Current number of BSS nodes
        seed: Random seed for deterministic selection
    
    Returns:
        Updated (idx2label, node_types, labels)
    """
    rng = random.Random(seed)
    
    # Find indices of nodes that can be converted
    # Exclude depot (D) and fixed intersections (1, 2)
    protected_labels = {"D", "1", "2"}
    
    # Collect current BSS and intersection nodes (excluding protected)
    bss_indices: List[int] = []
    intersection_indices: List[int] = []
    
    for idx, label in enumerate(labels):
        if label in protected_labels:
            continue
        node_type = node_types.get(label, "intersection")
        if node_type == "bss":
            bss_indices.append(idx)
        elif node_type == "intersection":
            intersection_indices.append(idx)
    
    diff = target_bss - baseline_bss
    
    if diff == 0:
        # No change needed
        return idx2label, node_types, labels
    
    # Create copies to modify
    new_idx2label = idx2label.copy()
    new_node_types = node_types.copy()
    new_labels = labels.copy()
    
    if diff > 0:
        # Need to convert intersections to BSS
        if len(intersection_indices) < diff:
            raise ValueError(
                f"Cannot convert {diff} intersections to BSS: only {len(intersection_indices)} "
                f"intersection nodes available (excluding protected nodes 1, 2)."
            )
        
        # Deterministic selection: shuffle and take first N
        candidates = list(intersection_indices)
        rng.shuffle(candidates)
        to_convert = candidates[:diff]
        
        # Relabel each converted node
        bss_counter = baseline_bss + 1
        for idx in sorted(to_convert):
            old_label = new_labels[idx]
            new_label = f"BSS{bss_counter}"
            bss_counter += 1
            
            # Update all data structures
            new_idx2label[idx] = new_label
            new_node_types[new_label] = "bss"
            del new_node_types[old_label]
            new_labels[idx] = new_label
            
            # Update graph nodes
            if old_label in graph["nodes"]:
                graph["nodes"][new_label] = graph["nodes"].pop(old_label)
            
            # Update graph edges
            for edge in graph["edges"]:
                if edge["from"] == old_label:
                    edge["from"] = new_label
                if edge["to"] == old_label:
                    edge["to"] = new_label
    
    else:
        # Need to convert BSS back to intersections
        diff_abs = abs(diff)
        if len(bss_indices) < diff_abs:
            raise ValueError(
                f"Cannot convert {diff_abs} BSS to intersections: only {len(bss_indices)} "
                f"BSS nodes available."
            )
        
        # Ensure at least 1 BSS remains
        if len(bss_indices) - diff_abs < 1:
            raise ValueError(
                f"Cannot convert {diff_abs} BSS to intersections: would leave less than 1 BSS."
            )
        
        # Deterministic selection: shuffle and take first N
        candidates = list(bss_indices)
        rng.shuffle(candidates)
        to_convert = candidates[:diff_abs]
        
        # Relabel each converted node
        # Find highest existing intersection number to continue counting
        intersection_counter = 1
        for label in new_labels:
            if label not in protected_labels and new_node_types.get(label) == "intersection":
                try:
                    num = int(label)
                    intersection_counter = max(intersection_counter, num + 1)
                except ValueError:
                    pass
        
        # Ensure new labels don't conflict with any existing labels
        for idx in sorted(to_convert):
            old_label = new_labels[idx]
            # Find next available intersection number
            new_label = None
            while new_label is None:
                candidate_label = str(intersection_counter)
                # Check if this label already exists (shouldn't for intersections, but be safe)
                if candidate_label not in new_node_types:
                    new_label = candidate_label
                intersection_counter += 1
            
            # Update all data structures
            new_idx2label[idx] = new_label
            new_node_types[new_label] = "intersection"
            del new_node_types[old_label]
            new_labels[idx] = new_label
            
            # Update graph nodes
            if old_label in graph["nodes"]:
                graph["nodes"][new_label] = graph["nodes"].pop(old_label)
            
            # Update graph edges
            for edge in graph["edges"]:
                if edge["from"] == old_label:
                    edge["from"] = new_label
                if edge["to"] == old_label:
                    edge["to"] = new_label
    
    return new_idx2label, new_node_types, new_labels


def _copy_depot_edge_values(
    graph: Dict[str, Any],
    labels: List[str],
    distance: MatrixF,
    traffic: MatrixF,
) -> None:
    edge_d1 = next(
        (edge for edge in graph["edges"] if edge["from"] == "D" and edge["to"] == "1"),
        None,
    )
    edge_d2 = next(
        (edge for edge in graph["edges"] if edge["from"] == "D" and edge["to"] == "2"),
        None,
    )
    if edge_d1 is None or edge_d2 is None:
        return

    edge_d1["distance"] = edge_d2["distance"]
    edge_d1["traffic_factor"] = edge_d2["traffic_factor"]

    idx_d = labels.index("D")
    idx_1 = labels.index("1")
    idx_2 = labels.index("2")
    distance[idx_d][idx_1] = distance[idx_d][idx_2]
    distance[idx_1][idx_d] = distance[idx_2][idx_d]
    traffic[idx_d][idx_1] = traffic[idx_d][idx_2]
    traffic[idx_1][idx_d] = traffic[idx_2][idx_d]


def _collect_eligible_edge_pairs(adj: MatrixI, labels: Sequence[str]) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    for i in range(len(adj)):
        for j in range(i + 1, len(adj)):
            if adj[i][j] == 1:
                if labels[i] == "D" or labels[j] == "D":
                    continue
                pairs.append((i, j))
    return pairs


def _select_electric_pairs(
    eligible_pairs: Sequence[Tuple[int, int]],
    electric_ratio: float,
    rng: random.Random,
) -> List[Tuple[int, int]]:
    if not eligible_pairs or electric_ratio <= 0.0:
        return []

    count = int(round(len(eligible_pairs) * electric_ratio))
    if electric_ratio > 0.0:
        count = max(1, count)
    count = min(count, len(eligible_pairs))

    shuffled = list(eligible_pairs)
    rng.shuffle(shuffled)
    return sorted(shuffled[:count])


def _apply_electric_traffic_override(
    traffic: MatrixF,
    electric_pairs: Sequence[Tuple[int, int]],
    value: float,
) -> None:
    for i, j in electric_pairs:
        traffic[i][j] = value
        traffic[j][i] = value


def _build_eroad_matrix(
    n_nodes: int,
    electric_pairs: Sequence[Tuple[int, int]],
    directed: bool,
) -> MatrixI:
    matrix = [[0 for _ in range(n_nodes)] for _ in range(n_nodes)]
    for i, j in electric_pairs:
        matrix[i][j] = 1
        if not directed:
            matrix[j][i] = 1
    return matrix


def _build_indicator_vectors(idx2label: IdxToLabel, base_size: int) -> Tuple[List[int], List[int]]:
    """
    Build station and customer indicator vectors.
    
    Args:
        idx2label: Mapping from index to node label
        base_size: Base size (should match len(labels) from build_graph_with_matrices)
    
    Returns:
        Tuple of (station_vector, customer_vector) each of length base_size + 1
    """
    station_vector = [0] * base_size
    customer_vector = [0] * base_size
    for idx in range(base_size):
        label = idx2label.get(idx, "")
        if label.upper().startswith("BSS"):
            station_vector[idx] = 1
        if label.upper().startswith("C"):
            customer_vector[idx] = 1
    # Add trailing 0 to match matrix dimensions after transformation (N+1 for CPLEX indexing)
    station_vector.append(0)
    customer_vector.append(0)
    return station_vector, customer_vector


def _map_label_to_ga(label: str) -> str:
    if label == "D":
        return "D"
    if label.startswith("C") and label[1:].isdigit():
        return f"L{label[1:]}"
    if label.startswith("BSS") and label[3:].isdigit():
        return f"CS{label[3:]}"
    return label


def _map_node_type_to_ga(node_type: str) -> str:
    if node_type == "depot":
        return "depot"
    if node_type == "customer":
        return "customer"
    if node_type == "bss":
        return "charging_station"
    return "intersection"


def _build_ga_payload(
    labels: Sequence[str],
    node_types: NodeTypes,
    distance: MatrixF,
    traffic: MatrixF,
    electric_pairs: Sequence[Tuple[int, int]],
) -> Dict[str, Any]:
    ga_nodes: List[Dict[str, Any]] = []
    label_map = {label: _map_label_to_ga(label) for label in labels}
    electric_set = set(electric_pairs)

    for label in labels:
        ga_nodes.append(
            {
                "id": label_map[label],
                "type": _map_node_type_to_ga(node_types.get(label, "intersection")),
            }
        )

    ga_edges: List[Dict[str, Any]] = []
    n = len(labels)
    for i in range(n):
        for j in range(i + 1, n):
            if distance[i][j] <= 0.0:
                continue
            edge_type = "electric" if (i, j) in electric_set else "normal"
            tf = 1.0 if edge_type == "electric" else float(traffic[i][j])
            ga_edges.append(
                {
                    "from": label_map[labels[i]],
                    "to": label_map[labels[j]],
                    "distance": round(float(distance[i][j]), 2),
                    "traffic_factor": round(tf, 2),
                    "type": edge_type,
                }
            )

    payload = {
        "nodes": ga_nodes,
        "edges": ga_edges,
        "base_speed": 50,
        "initial_battery_percent": 100,
        "starting_node": "D",
        "battery_capacity": 100,
        "vehicle_mass": 1800,
        "rolling_resistance": 0.01,
        "drag_coefficient": 0.6,
        "cross_sectional_area": 3.5,
        "mass_factor": 1.1,
        "package_weight": 5,
        "charging_power": 100,
        "charging_efficiency": 0.95,
        "dwc_power": 20,
        "dwc_efficiency": 0.85,
        "electric_road_speed": 50,
        "air_density": 1.205,
        "angle": 0.86,
    }
    return payload


def _validate_ga_payload(payload: Dict[str, Any]) -> None:
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("GA payload has no nodes.")
    if not isinstance(edges, list) or not edges:
        raise ValueError("GA payload has no edges.")

    node_ids = {node["id"] for node in nodes}
    if "D" not in node_ids:
        raise ValueError("GA payload is missing depot node 'D'.")

    customer_count = sum(1 for node in nodes if node.get("type") == "customer")
    station_count = sum(1 for node in nodes if node.get("type") == "charging_station")
    if customer_count == 0:
        raise ValueError("GA payload has no customer nodes.")
    if station_count == 0:
        raise ValueError("GA payload has no charging_station nodes.")

    for edge in edges:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError("GA payload edge references unknown node IDs.")


def _write_json(output_path: str, payload: Dict[str, Any]) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def _write_dat(
    output_path: str,
    total_nodes: int,
    station_vector: Sequence[int],
    customer_vector: Sequence[int],
    adj: MatrixI,
    dist: MatrixF,
    trav: MatrixF,
    edep: MatrixF,
    ebox: MatrixF,
    eroad: MatrixI,
) -> None:
    # Visits follows current project convention: number of customer nodes + 1.
    # Exclude trailing element (always 0) from count
    visits = max(1, int(sum(customer_vector[:-1])) + 1)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Initial = 100; // Initial energy level at the depot\n")
        f.write("Eth = 20;\t// Minimum energy level\n\n")
        f.write("S = 0;\t\t// Sourse of EV\n")
        f.write(f"D = {total_nodes};\t\t// Destination of EV\n")
        f.write("G = 10000;  // Large value\n\n")
        f.write(f"Nodes = {total_nodes};\n")
        f.write(f"Visits = {visits};\n\n")
        f.write("ECharging = 1;\t\t// Vehicle charging per time unit\n")
        f.write("Reroad = 3;\t\t\t// E-road Charging rate per time unit\n\n")
        f.write(f"Station = {list(station_vector)};\n")
        f.write(f"Costumer = {list(customer_vector)};\n\n")

        f.write("Adj = \t[\n")
        f.write(_format_matrix_for_dat(adj))
        f.write("\n];\n\n")

        f.write("Trav =\t[\n")
        f.write(_format_matrix_for_dat(trav, decimals=2))
        f.write("\n];\n\n")

        f.write("Dist =\t[\n")
        f.write(_format_matrix_for_dat(dist, decimals=2))
        f.write("\n];\n\n")

        f.write("Edep =\t[\n")
        f.write(_format_matrix_for_dat(edep, decimals=2))
        f.write("\n];\n\n")

        f.write("Ebox =\t[\n")
        f.write(_format_matrix_for_dat(ebox, decimals=2))
        f.write("\n];\n\n")

        f.write("Eroad = [\t")
        f.write(_format_matrix_for_dat(eroad))
        f.write("\n];\n")


def _format_matrix_for_dat(matrix: Sequence[Sequence[Any]], decimals: Optional[int] = None) -> str:
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
        lines.append(f"[{', '.join(rendered)}]{suffix}")
    return "\n\t\t\t".join(lines)


def _write_summary(
    output_path: str,
    total_nodes: int,
    num_customers: int,
    num_bss: int,
    seed: Optional[int],
    electric_ratio: float,
    cs_ratio: float,
    ga_payload: Dict[str, Any],
    electric_pairs: Sequence[Tuple[int, int]],
) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== UIG2 INSTANCE SUMMARY ===\n")
        f.write(f"Total Nodes: {total_nodes}\n")
        f.write(f"Customers: {num_customers}\n")
        f.write(f"Charging Stations: {num_bss}\n")
        f.write(f"Charging Station Ratio: {cs_ratio:.3f}\n")
        f.write(f"Seed: {seed}\n")
        f.write(f"Electric Edge Ratio: {electric_ratio:.3f}\n")
        f.write(f"Electric Edges Count: {len(electric_pairs)}\n\n")

        f.write("=== GA NODE COUNTS ===\n")
        nodes = ga_payload["nodes"]
        f.write(f"All Nodes: {len(nodes)}\n")
        f.write(f"Customers: {sum(1 for n in nodes if n['type'] == 'customer')}\n")
        f.write(f"Charging Stations: {sum(1 for n in nodes if n['type'] == 'charging_station')}\n")
        f.write(f"Intersections: {sum(1 for n in nodes if n['type'] == 'intersection')}\n")
        f.write(f"Edges: {len(ga_payload['edges'])}\n")
        f.write(f"Electric Edges: {sum(1 for e in ga_payload['edges'] if e['type'] == 'electric')}\n")


def _generate_visualization(graph: Dict[str, Any], output_path: str) -> None:
    if visualize_graph is None:
        return
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
    except Exception:
        # Visualization is best effort; failures should not block instance generation.
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate UIG2 project-2 input artifacts.")
    parser.add_argument("total_nodes", type=int, help="Total number of nodes (>= 4).")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    parser.add_argument(
        "--electric-ratio",
        type=float,
        default=0.2,
        help="Ratio of eligible edges to mark as electric in [0, 1].",
    )
    parser.add_argument(
        "--eroad-ratio",
        type=float,
        default=None,
        help="Alias for --electric-ratio. If both given, --eroad-ratio wins.",
    )
    parser.add_argument(
        "--cs-ratio",
        type=float,
        default=None,
        help="Override charging-station ratio of total nodes in [0.05, 0.5]. Default uses compute_counts (0.2).",
    )
    args = parser.parse_args()

    # Resolve electric_ratio: --eroad-ratio takes precedence over --electric-ratio
    electric_ratio = args.eroad_ratio if args.eroad_ratio is not None else args.electric_ratio

    outputs = generate_uig2_network(
        total_nodes=args.total_nodes,
        seed=args.seed,
        electric_ratio=electric_ratio,
        cs_ratio=args.cs_ratio,
    )

    print("UIG2 artifacts saved:")
    print(f"  - JSON: {outputs['json']}")
    print(f"  - DAT:  {outputs['dat']}")
    print(f"  - TXT:  {outputs['summary']}")
    print(f"  - PNG:  {outputs['visualization']}")


if __name__ == "__main__":
    main()

