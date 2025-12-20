"""
Traffic Factor Modifier

Modifies traffic_factor values in both .dat and .json files within a specified range,
maintaining consistency by updating Trav, Edep, and Ebox matrices proportionally.
"""

import json
import re
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional


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
    changes: Dict[Tuple[str, str], Tuple[float, float]],
    label_to_index: Dict[str, int]
) -> None:
    """
    Update Trav, Edep, and Ebox matrices based on traffic factor changes.
    Uses ratio: old_tf / new_tf to scale values.
    """
    for (from_node, to_node), (old_tf, new_tf) in changes.items():
        if from_node not in label_to_index or to_node not in label_to_index:
            continue
        
        i = label_to_index[from_node]
        j = label_to_index[to_node]
        
        # Calculate ratio (inverse relationship: higher traffic = slower)
        if new_tf > 0:
            ratio = old_tf / new_tf
        else:
            ratio = 1.0
        
        # Update matrices if they have non-zero values
        if i < len(Trav) and j < len(Trav[i]) and Trav[i][j] != 0.0:
            Trav[i][j] = round(Trav[i][j] * ratio, 2)
        
        if i < len(Edep) and j < len(Edep[i]) and Edep[i][j] != 0.0:
            Edep[i][j] = round(Edep[i][j] * ratio, 2)
        
        if i < len(Ebox) and j < len(Ebox[i]) and Ebox[i][j] != 0.0:
            Ebox[i][j] = round(Ebox[i][j] * ratio, 2)
        
        # Also update reverse direction for undirected edges
        if j < len(Trav) and i < len(Trav[j]) and Trav[j][i] != 0.0:
            Trav[j][i] = round(Trav[j][i] * ratio, 2)
        
        if j < len(Edep) and i < len(Edep[j]) and Edep[j][i] != 0.0:
            Edep[j][i] = round(Edep[j][i] * ratio, 2)
        
        if j < len(Ebox) and i < len(Ebox[j]) and Ebox[j][i] != 0.0:
            Ebox[j][i] = round(Ebox[j][i] * ratio, 2)


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
    
    # Update matrices in .dat file
    update_dat_matrices(Trav, Edep, Ebox, changes, label_to_index)
    
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

