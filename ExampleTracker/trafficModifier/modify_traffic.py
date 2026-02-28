"""
Traffic Factor Modifier

Modifies traffic_factor values in both .dat and .json files within a specified range,
recalculating Trav (travel time), Edep (energy depletion), and Ebox matrices using
physics-based energy consumption model.
"""

import json
import re
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Default physics constants
DEFAULT_ANGLE = 0.86  # degrees
DEFAULT_AIR_DENSITY = 1.205  # kg/m³
GRAVITY = 9.8  # m/s²


def calculate_actual_speed(base_speed: float, traffic_factor: float, current_load: float = 0) -> float:
    """
    Calculate actual speed based on base speed and traffic factor.
    
    Args:
        base_speed: Base speed in km/h
        traffic_factor: Traffic factor (0-1, where 1 = free flow)
        current_load: Current payload in kg (affects speed slightly)
    
    Returns:
        Actual speed in km/h
    """
    # Speed is proportional to traffic factor
    return base_speed * traffic_factor


def calculate_energy_consumption(
    distance: float,
    actual_speed: float,
    vehicle_mass: float,
    rolling_resistance: float,
    drag_coefficient: float,
    cross_sectional_area: float,
    mass_factor: float,
    current_load: float = 0,
    angle: float = DEFAULT_ANGLE,
    air_density: float = DEFAULT_AIR_DENSITY
) -> float:
    """
    Calculate energy consumption using physics-based model.
    
    Energy = (1/3600) × [Total_Mass × g × (f×cos(α) + sin(α)) + 
                         0.0386×ρ×c×A×v₀² + 
                         (Total_Mass + m)×dv_dt] × distance
    
    Args:
        distance: Distance in km
        actual_speed: Actual speed in km/h
        vehicle_mass: Base vehicle mass in kg
        rolling_resistance: Rolling resistance coefficient (f)
        drag_coefficient: Drag coefficient (Cx)
        cross_sectional_area: Cross-sectional area in m² (A)
        mass_factor: Mass factor for acceleration (m)
        current_load: Current payload in kg
        angle: Road grade angle in degrees
        air_density: Air density in kg/m³
    
    Returns:
        Energy consumption in kWh
    """
    # Convert angle to radians
    cos_alpha = math.cos(math.radians(angle))
    sin_alpha = math.sin(math.radians(angle))
    
    # Calculate dv_dt based on speed ranges
    if 50 <= actual_speed <= 80:
        dv_dt = 0.3
    elif 81 <= actual_speed <= 120:
        dv_dt = 2
    else:
        dv_dt = 0
    
    # Total mass including load
    total_mass = vehicle_mass + current_load
    
    # Energy consumption formula
    # Rolling resistance + grade resistance
    resistance_term = total_mass * GRAVITY * (rolling_resistance * cos_alpha + sin_alpha)
    
    # Aerodynamic drag (speed-squared relationship)
    aero_term = 0.0386 * air_density * drag_coefficient * cross_sectional_area * (actual_speed ** 2)
    
    # Acceleration term
    accel_term = (total_mass + mass_factor) * dv_dt
    
    # Total energy (divide by 3600 to convert to kWh)
    energy_consumption = (1 / 3600) * (resistance_term + aero_term + accel_term) * distance
    
    return energy_consumption


def calculate_energy_per_box(
    base_energy: float,
    vehicle_mass: float,
    box_weight: float = 100.0
) -> float:
    """
    Calculate additional energy consumption per box/package.
    
    Uses mass ratio approach: energy per box is proportional to the ratio
    of box weight to vehicle mass, applied to the base energy.
    
    Ebox = base_energy × (box_weight / vehicle_mass)
    
    This gives values consistent with typical vehicle routing problems where
    Ebox represents the additional energy cost of carrying payload.
    
    Args:
        base_energy: Base energy consumption without load (Edep) in kWh
        vehicle_mass: Base vehicle mass in kg
        box_weight: Weight of payload per box in kg (default: 100 kg)
    
    Returns:
        Additional energy per box in kWh
    """
    # Energy per box is proportional to mass ratio
    # This captures the fact that heavier loads require more energy
    mass_ratio = box_weight / vehicle_mass
    
    return base_energy * mass_ratio


def calculate_travel_time(distance: float, actual_speed: float) -> float:
    """
    Calculate travel time in minutes.
    
    Args:
        distance: Distance in km
        actual_speed: Actual speed in km/h
    
    Returns:
        Travel time in minutes
    """
    if actual_speed <= 0:
        return float('inf')
    return (distance / actual_speed) * 60  # Convert hours to minutes


def build_node_mapping(json_data: dict) -> Dict[str, int]:
    """
    Build a mapping from JSON node names to matrix indices.
    The order in the JSON nodes dict determines the index.
    """
    label_to_index = {}
    for idx, node_name in enumerate(json_data["nodes"].keys()):
        label_to_index[node_name] = idx
    return label_to_index


def parse_dat_file(dat_path: Path) -> Tuple[Dict[str, any], List[List[float]], List[List[float]], List[List[float]]]:
    """
    Parse .dat file and extract header info and matrices.
    Returns: (header_info, Trav, Edep, Ebox)
    """
    content = dat_path.read_text(encoding="utf-8")
    
    # Extract header information (everything before matrices)
    header_match = re.search(r'^(.*?)Adj\s*=\s*\[', content, re.DOTALL)
    header_info = header_match.group(1) if header_match else ""
    
    # Extract Adj matrix (for reference, but we don't modify it)
    adj_match = re.search(r'Adj\s*=\s*\[(.*?)\];', content, re.DOTALL)
    
    # Extract Trav matrix
    trav_match = re.search(r'Trav\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not trav_match:
        raise ValueError("Could not find Trav matrix in .dat file")
    
    # Extract Edep matrix
    edep_match = re.search(r'Edep\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not edep_match:
        raise ValueError("Could not find Edep matrix in .dat file")
    
    # Extract Ebox matrix
    ebox_match = re.search(r'Ebox\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not ebox_match:
        raise ValueError("Could not find Ebox matrix in .dat file")
    
    # Parse matrices
    Trav = _parse_matrix(trav_match.group(1))
    Edep = _parse_matrix(edep_match.group(1))
    Ebox = _parse_matrix(ebox_match.group(1))
    
    # Get everything after Ebox for footer
    footer_start = ebox_match.end()
    footer_info = content[footer_start:].strip()
    
    header_info_dict = {
        "header": header_info,
        "adj_section": adj_match.group(0) if adj_match else "",
        "footer": footer_info
    }
    
    return header_info_dict, Trav, Edep, Ebox


def _parse_matrix(matrix_str: str) -> List[List[float]]:
    """Parse a matrix string into a 2D list of floats."""
    matrix = []
    # Split by lines and parse each row
    lines = matrix_str.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Extract values from [value1, value2, ...] format
        row_match = re.search(r'\[(.*?)\]', line)
        if row_match:
            values_str = row_match.group(1)
            # Split by comma and convert to float
            values = [float(v.strip()) for v in values_str.split(',') if v.strip()]
            matrix.append(values)
    return matrix


def modify_traffic_factors(
    json_data: dict,
    lower_bound: float,
    upper_bound: float,
    seed: Optional[int] = None
) -> Dict[Tuple[str, str], Tuple[float, float]]:
    """
    Modify traffic factors in JSON edges within the specified range.
    Returns: dict mapping (from, to) -> (old_tf, new_tf)
    """
    if seed is not None:
        random.seed(seed)
    
    if not (0 < lower_bound <= upper_bound <= 1.0):
        raise ValueError("Traffic factor bounds must satisfy: 0 < lower <= upper <= 1.0")
    
    changes = {}
    
    for edge in json_data["edges"]:
        old_tf = edge["traffic_factor"]
        new_tf = round(random.uniform(lower_bound, upper_bound), 2)
        edge["traffic_factor"] = new_tf
        changes[(edge["from"], edge["to"])] = (old_tf, new_tf)
    
    return changes


def update_dat_matrices(
    Trav: List[List[float]],
    Edep: List[List[float]],
    Ebox: List[List[float]],
    json_data: dict,
    label_to_index: Dict[str, int]
) -> None:
    """
    Update Trav, Edep, and Ebox matrices using physics-based calculations.
    
    Calculates:
    - Trav: Travel time based on distance / actual_speed
    - Edep: Energy consumption using physics formula
    - Ebox: Additional energy per box
    """
    # Extract vehicle parameters from JSON
    vehicle = json_data.get("vehicle", {})
    vehicle_mass = vehicle.get("base_mass", 1500)
    rolling_resistance = vehicle.get("f", 0.01)
    drag_coefficient = vehicle.get("Cx", 0.3)
    cross_sectional_area = vehicle.get("A", 2.5)
    mass_factor = vehicle.get("m", 100)
    base_speed = json_data.get("base_speed", 50)
    
    # Build edge lookup for quick access
    edge_lookup = {}
    for edge in json_data["edges"]:
        edge_lookup[(edge["from"], edge["to"])] = edge
        # Also store reverse for bidirectional edges
        edge_lookup[(edge["to"], edge["from"])] = edge
    
    # Update matrices for each edge
    for edge in json_data["edges"]:
        from_node = edge["from"]
        to_node = edge["to"]
        distance = edge["distance"]
        traffic_factor = edge["traffic_factor"]
        
        if from_node not in label_to_index or to_node not in label_to_index:
            continue
        
        i = label_to_index[from_node]
        j = label_to_index[to_node]
        
        # Calculate actual speed based on traffic factor
        actual_speed = calculate_actual_speed(base_speed, traffic_factor)
        
        # Calculate travel time (minutes)
        travel_time = calculate_travel_time(distance, actual_speed)
        
        # Calculate energy consumption (kWh)
        energy = calculate_energy_consumption(
            distance=distance,
            actual_speed=actual_speed,
            vehicle_mass=vehicle_mass,
            rolling_resistance=rolling_resistance,
            drag_coefficient=drag_coefficient,
            cross_sectional_area=cross_sectional_area,
            mass_factor=mass_factor
        )
        
        # Calculate energy per box (kWh) using mass ratio approach
        # Ebox = Edep × (box_weight / vehicle_mass)
        # With 250 kg and 1500 kg vehicle, ratio ≈ 16.7% which matches original data
        energy_per_box = calculate_energy_per_box(
            base_energy=energy,
            vehicle_mass=vehicle_mass,
            box_weight=250.0  # 250 kg per box gives ~16-17% of Edep
        )
        
        # Update forward direction
        if i < len(Trav) and j < len(Trav[i]):
            Trav[i][j] = round(travel_time, 2)
        
        if i < len(Edep) and j < len(Edep[i]):
            Edep[i][j] = round(energy, 2)
        
        if i < len(Ebox) and j < len(Ebox[i]):
            Ebox[i][j] = round(energy_per_box, 2)
        
        # Update reverse direction (for undirected edges)
        if j < len(Trav) and i < len(Trav[j]):
            Trav[j][i] = round(travel_time, 2)
        
        if j < len(Edep) and i < len(Edep[j]):
            Edep[j][i] = round(energy, 2)
        
        if j < len(Ebox) and i < len(Ebox[j]):
            Ebox[j][i] = round(energy_per_box, 2)


def format_matrix_for_dat(matrix: List[List[float]], decimals: int = 2) -> str:
    """Format a matrix for writing to .dat file."""
    lines = []
    for i, row in enumerate(matrix):
        formatted_values = [f"{val:.{decimals}f}" for val in row]
        suffix = "," if i < len(matrix) - 1 else ""
        lines.append(f" [{', '.join(formatted_values)}]{suffix}")
    return "\n".join(lines)


def write_dat_file(
    output_path: Path,
    header_info: Dict[str, str],
    Trav: List[List[float]],
    Edep: List[List[float]],
    Ebox: List[List[float]]
) -> None:
    """Write modified .dat file with updated matrices."""
    with output_path.open("w", encoding="utf-8") as f:
        # Write header
        f.write(header_info["header"])
        
        # Write Adj section
        f.write(header_info["adj_section"])
        f.write("\n\n")
        
        # Write Trav matrix
        f.write("Trav =\t[\n")
        f.write(format_matrix_for_dat(Trav))
        f.write("\n];\n\n")
        
        # Write Edep matrix
        f.write("Edep =\t[\n")
        f.write(format_matrix_for_dat(Edep))
        f.write("\n];\n\n")
        
        # Write Ebox matrix
        f.write("Ebox =\t[\n")
        f.write(format_matrix_for_dat(Ebox))
        f.write("\n];")
        
        # Write footer if exists
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
    """
    Main function to modify traffic factors in both .dat and .json files.
    
    Args:
        dat_path: Path to input .dat file
        json_path: Path to input .json file
        lower_bound: Lower bound for traffic factors (default: 0.6)
        upper_bound: Upper bound for traffic factors (default: 0.9)
        seed: Optional random seed for reproducibility
        output_dir: Optional output directory (default: same as input files)
    
    Returns:
        Tuple of (output_dat_path, output_json_path)
    """
    # Determine output paths
    if output_dir is None:
        output_dir = dat_path.parent
    
    output_dat_path = output_dir / f"{dat_path.stem}_modified{dat_path.suffix}"
    output_json_path = output_dir / f"{json_path.stem}_modified{json_path.suffix}"
    
    # Load JSON file
    with json_path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    # Build node mapping
    label_to_index = build_node_mapping(json_data)
    
    # Parse .dat file
    header_info, Trav, Edep, Ebox = parse_dat_file(dat_path)
    
    # Modify traffic factors in JSON
    changes = modify_traffic_factors(json_data, lower_bound, upper_bound, seed)
    
    # Update matrices in .dat file using physics-based calculations
    update_dat_matrices(Trav, Edep, Ebox, json_data, label_to_index)
    
    # Write modified JSON file
    with output_json_path.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
        f.write("\n")
    
    # Write modified .dat file
    write_dat_file(output_dat_path, header_info, Trav, Edep, Ebox)
    
    print(f"Modified files created:")
    print(f"  - {output_dat_path}")
    print(f"  - {output_json_path}")
    print(f"Traffic factors modified: {len(changes)} edges")
    print(f"Range: [{lower_bound}, {upper_bound}]")
    
    return output_dat_path, output_json_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Modify traffic factors in .dat and .json files"
    )
    parser.add_argument(
        "--dat",
        type=Path,
        default=Path("10c_5bss_24total.dat"),
        help="Path to input .dat file (default: 10c_5bss_24total.dat)"
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("10c_5bss_24total.json"),
        help="Path to input .json file (default: 10c_5bss_24total.json)"
    )
    parser.add_argument(
        "--lower",
        type=float,
        default=0.6,
        help="Lower bound for traffic factors (default: 0.6)"
    )
    parser.add_argument(
        "--upper",
        type=float,
        default=0.9,
        help="Upper bound for traffic factors (default: 0.9)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: same as input files)"
    )
    
    args = parser.parse_args()
    
    # Resolve paths - try script directory first, then current directory
    script_dir = Path(__file__).parent
    if args.dat.is_absolute():
        dat_path = args.dat
    elif (script_dir / args.dat).exists():
        dat_path = script_dir / args.dat
    else:
        dat_path = Path(args.dat).resolve()
    
    if args.json.is_absolute():
        json_path = args.json
    elif (script_dir / args.json).exists():
        json_path = script_dir / args.json
    else:
        json_path = Path(args.json).resolve()
    
    if args.output_dir:
        output_dir = args.output_dir if args.output_dir.is_absolute() else Path(args.output_dir).resolve()
    else:
        output_dir = None
    
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
        output_dir=output_dir
    )

