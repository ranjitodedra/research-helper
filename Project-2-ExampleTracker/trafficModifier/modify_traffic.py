"""
Traffic Factor Modifier for Project-2 (C&G) Format

Modifies traffic_factor values in both .dat and .json files within a specified range,
recalculating Trav, Edep, and Ebox matrices using a physics-based energy consumption model.

Handles the V3 JSON format (array-based nodes, edge types, flat vehicle params)
and the corresponding DAT format (with Dist, Eroad matrices).

Electric edges (type="electric") are left untouched for fair comparison.
"""

import json
import re
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional


DEFAULT_ANGLE = 0.86  # degrees
DEFAULT_AIR_DENSITY = 1.205  # kg/m³
GRAVITY = 9.8  # m/s²


def calculate_actual_speed(base_speed: float, traffic_factor: float) -> float:
    return base_speed * traffic_factor


def calculate_energy_consumption(
    distance: float,
    actual_speed: float,
    vehicle_mass: float,
    rolling_resistance: float,
    drag_coefficient: float,
    cross_sectional_area: float,
    mass_factor: float,
    angle: float = DEFAULT_ANGLE,
    air_density: float = DEFAULT_AIR_DENSITY
) -> float:
    """
    Energy = (1/3600) × [Total_Mass × g × (f×cos(α) + sin(α)) +
                         0.0386×ρ×c×A×v₀² +
                         (Total_Mass + m)×dv_dt] × distance
    """
    cos_alpha = math.cos(math.radians(angle))
    sin_alpha = math.sin(math.radians(angle))

    if 50 <= actual_speed <= 80:
        dv_dt = 0.3
    elif 81 <= actual_speed <= 120:
        dv_dt = 2
    else:
        dv_dt = 0

    resistance_term = vehicle_mass * GRAVITY * (rolling_resistance * cos_alpha + sin_alpha)
    aero_term = 0.0386 * air_density * drag_coefficient * cross_sectional_area * (actual_speed ** 2)
    accel_term = (vehicle_mass + mass_factor) * dv_dt

    energy = (1 / 3600) * (resistance_term + aero_term + accel_term) * distance
    return energy


def calculate_energy_per_box(
    base_energy: float,
    vehicle_mass: float,
    box_weight: float = 250.0
) -> float:
    """
    Ebox = base_energy × (box_weight / vehicle_mass)

    box_weight is the effective load weight used for Ebox scaling, NOT the
    individual package_weight from the JSON (which is typically much smaller).
    Default 250 kg produces ~14% ratio matching original data.
    """
    return base_energy * (box_weight / vehicle_mass)


def calculate_travel_time(distance: float, actual_speed: float) -> float:
    if actual_speed <= 0:
        return float('inf')
    return (distance / actual_speed) * 60


def build_node_mapping(json_data: dict) -> Dict[str, int]:
    """
    Build mapping from node id to matrix index.
    V3 format: nodes is a list of {"id": ..., "type": ...}.
    """
    label_to_index = {}
    for idx, node in enumerate(json_data["nodes"]):
        label_to_index[node["id"]] = idx
    return label_to_index


def parse_dat_file(dat_path: Path) -> Tuple[dict, dict]:
    """
    Parse V3 .dat file. Returns (header_info, matrices) where matrices is a
    dict keyed by matrix name -> 2D list of floats.
    """
    content = dat_path.read_text(encoding="utf-8")

    header_match = re.search(r'^(.*?)Adj\s*=\s*', content, re.DOTALL)
    header_text = header_match.group(1) if header_match else ""

    matrix_names = ["Adj", "Trav", "Dist", "Edep", "Ebox", "Eroad"]
    matrices = {}
    matrix_sections = {}

    for name in matrix_names:
        pattern = rf'{name}\s*=\s*\[(.*?)\];'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            matrices[name] = _parse_matrix(match.group(1))
            matrix_sections[name] = match

    last_match = max(matrix_sections.values(), key=lambda m: m.end())
    footer_text = content[last_match.end():].strip()

    return {
        "header": header_text,
        "footer": footer_text,
        "matrix_order": [n for n in matrix_names if n in matrices],
    }, matrices


def _parse_matrix(matrix_str: str) -> List[List[float]]:
    matrix = []
    for line in matrix_str.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        row_match = re.search(r'\[(.*?)\]', line)
        if row_match:
            values = [float(v.strip()) for v in row_match.group(1).split(',') if v.strip()]
            matrix.append(values)
    return matrix


def modify_traffic_factors(
    json_data: dict,
    lower_bound: float,
    upper_bound: float,
    seed: Optional[int] = None
) -> Dict[Tuple[str, str], Tuple[float, float]]:
    """
    Modify traffic factors for normal edges only.
    Electric edges are left untouched.
    """
    if seed is not None:
        random.seed(seed)

    if not (0 < lower_bound <= upper_bound <= 1.0):
        raise ValueError("Traffic factor bounds must satisfy: 0 < lower <= upper <= 1.0")

    changes = {}
    for edge in json_data["edges"]:
        if edge.get("type") == "electric":
            continue
        old_tf = edge["traffic_factor"]
        new_tf = round(random.uniform(lower_bound, upper_bound), 2)
        edge["traffic_factor"] = new_tf
        changes[(edge["from"], edge["to"])] = (old_tf, new_tf)

    return changes


def update_dat_matrices(
    matrices: dict,
    json_data: dict,
    label_to_index: Dict[str, int]
) -> None:
    """
    Recalculate Trav, Edep, and Ebox from the (possibly modified) JSON edge data.
    Adj, Dist, and Eroad are kept as-is.
    """
    vm = json_data.get("vehicle_mass", 1800)
    rr = json_data.get("rolling_resistance", 0.01)
    dc = json_data.get("drag_coefficient", 0.6)
    csa = json_data.get("cross_sectional_area", 3.5)
    mf = json_data.get("mass_factor", 1.1)
    bs = json_data.get("base_speed", 50)
    angle = json_data.get("angle", DEFAULT_ANGLE)
    air_density = json_data.get("air_density", DEFAULT_AIR_DENSITY)

    Trav = matrices["Trav"]
    Edep = matrices["Edep"]
    Ebox = matrices["Ebox"]

    for edge in json_data["edges"]:
        from_node = edge["from"]
        to_node = edge["to"]

        if from_node not in label_to_index or to_node not in label_to_index:
            continue

        i = label_to_index[from_node]
        j = label_to_index[to_node]

        distance = edge["distance"]
        traffic_factor = edge["traffic_factor"]

        actual_speed = calculate_actual_speed(bs, traffic_factor)
        travel_time = calculate_travel_time(distance, actual_speed)
        energy = calculate_energy_consumption(
            distance=distance,
            actual_speed=actual_speed,
            vehicle_mass=vm,
            rolling_resistance=rr,
            drag_coefficient=dc,
            cross_sectional_area=csa,
            mass_factor=mf,
            angle=angle,
            air_density=air_density,
        )
        energy_per_box = calculate_energy_per_box(energy, vm)

        for r, c in [(i, j), (j, i)]:
            if r < len(Trav) and c < len(Trav[r]):
                Trav[r][c] = round(travel_time, 2)
            if r < len(Edep) and c < len(Edep[r]):
                Edep[r][c] = round(energy, 2)
            if r < len(Ebox) and c < len(Ebox[r]):
                Ebox[r][c] = round(energy_per_box, 2)


def sync_destination_copy(matrices: dict, header_text: str) -> None:
    """
    The DAT file has a virtual destination node (D) that mirrors the source
    depot (S).  After recalculating Trav/Edep/Ebox for edges from the JSON,
    copy values from the source depot row/column to the destination copy
    row/column so they stay consistent.
    """
    s_match = re.search(r'S\s*=\s*(\d+)', header_text)
    d_match = re.search(r'D\s*=\s*(\d+)', header_text)
    if not s_match or not d_match:
        return

    s_idx = int(s_match.group(1))
    d_idx = int(d_match.group(1))
    if s_idx == d_idx:
        return

    adj = matrices.get("Adj")
    if not adj:
        return

    n = len(adj)
    if d_idx >= n or s_idx >= n:
        return

    for name in ["Trav", "Edep", "Ebox"]:
        mat = matrices.get(name)
        if not mat:
            continue
        for j in range(n):
            if adj[d_idx][j] != 0 and adj[s_idx][j] != 0:
                mat[d_idx][j] = mat[s_idx][j]
                mat[j][d_idx] = mat[j][s_idx]


def format_matrix_for_dat(matrix: List[List[float]], decimals: int = 2, use_int: bool = False) -> str:
    lines = []
    for i, row in enumerate(matrix):
        if use_int:
            formatted = [str(int(v)) for v in row]
        else:
            formatted = [f"{v:.{decimals}f}" for v in row]
        suffix = "," if i < len(matrix) - 1 else ""
        lines.append(f"\t\t\t[{', '.join(formatted)}]{suffix}")
    return "\n".join(lines)


def write_dat_file(
    output_path: Path,
    header_info: dict,
    matrices: dict
) -> None:
    with output_path.open("w", encoding="utf-8") as f:
        f.write(header_info["header"])

        for name in header_info["matrix_order"]:
            mat = matrices[name]
            is_int = name in ("Adj", "Eroad")
            f.write(f"{name} =\t[\n")
            f.write(format_matrix_for_dat(mat, decimals=2, use_int=is_int))
            f.write("\n];\n\n")

        if header_info["footer"]:
            f.write(header_info["footer"])


def modify_traffic_files(
    dat_path: Path,
    json_path: Path,
    lower_bound: float = 0.6,
    upper_bound: float = 0.9,
    seed: Optional[int] = None,
    output_dir: Optional[Path] = None
) -> Tuple[Path, Path]:
    if output_dir is None:
        output_dir = dat_path.parent

    output_dat_path = output_dir / f"{dat_path.stem}_modified{dat_path.suffix}"
    output_json_path = output_dir / f"{json_path.stem}_modified{json_path.suffix}"

    with json_path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)

    label_to_index = build_node_mapping(json_data)
    header_info, matrices = parse_dat_file(dat_path)

    changes = modify_traffic_factors(json_data, lower_bound, upper_bound, seed)
    update_dat_matrices(matrices, json_data, label_to_index)
    sync_destination_copy(matrices, header_info["header"])

    with output_json_path.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
        f.write("\n")

    write_dat_file(output_dat_path, header_info, matrices)

    print(f"Modified files created:")
    print(f"  - {output_dat_path}")
    print(f"  - {output_json_path}")
    print(f"Traffic factors modified: {len(changes)} edges (normal only, electric untouched)")
    print(f"Range: [{lower_bound}, {upper_bound}]")
    if changes:
        print("\nChanges:")
        for (fr, to), (old, new) in changes.items():
            print(f"  {fr} -> {to}: {old} -> {new}")

    return output_dat_path, output_json_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Modify traffic factors in Project-2 (C&G) .dat and .json files"
    )
    parser.add_argument(
        "--dat", type=Path, required=True,
        help="Path to input .dat file"
    )
    parser.add_argument(
        "--json", type=Path, required=True,
        help="Path to input .json file"
    )
    parser.add_argument(
        "--lower", type=float, default=0.6,
        help="Lower bound for traffic factors (default: 0.6)"
    )
    parser.add_argument(
        "--upper", type=float, default=0.9,
        help="Upper bound for traffic factors (default: 0.9)"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory (default: same as input files)"
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent

    def resolve_path(p: Path) -> Path:
        if p.is_absolute():
            return p
        if (script_dir / p).exists():
            return script_dir / p
        return Path(p).resolve()

    dat_path = resolve_path(args.dat)
    json_path = resolve_path(args.json)
    output_dir = resolve_path(args.output_dir) if args.output_dir else None

    if not dat_path.exists():
        print(f"Error: .dat file not found: {dat_path}")
        exit(1)
    if not json_path.exists():
        print(f"Error: .json file not found: {json_path}")
        exit(1)

    modify_traffic_files(
        dat_path=dat_path,
        json_path=json_path,
        lower_bound=args.lower,
        upper_bound=args.upper,
        seed=args.seed,
        output_dir=output_dir,
    )
