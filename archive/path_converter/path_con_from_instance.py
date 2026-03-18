"""
Convert numeric node paths to labeled paths using mapping derived from instance files.

Use when you don't have a hand-written idx2label: this script builds the mapping
from the instance folder's JSON (and optionally .dat for depot/destination).

Usage:
  python path_con_from_instance.py <instance_folder> [path_string]
  python path_con_from_instance.py <instance_folder> --file <output_file.txt>
  python path_con_from_instance.py <instance_folder>   # read path(s) from stdin, one per line

Example (C&G_NodeChange/16):
  python path_con_from_instance.py "Project-2-ExampleTracker/C&G_NodeChange/16" "0->1->13->12->11->10->9->8->7->6->15->14->2->16"
"""

from pathlib import Path
import re
import json
import sys


def load_mapping_from_instance(instance_folder: str | Path) -> dict[int, str]:
    """
    Build idx2label from instance folder: JSON nodes (and .dat for S/D if present).
    """
    folder = Path(instance_folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Instance folder not found: {folder}")

    idx2label: dict[int, str] = {}

    # 1) Load from JSON (nodes array order = index 0, 1, 2, ...)
    json_files = list(folder.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No .json file found in {folder}")
    # Prefer *_V3.json or any .json
    data_file = next((f for f in json_files if "V3" in f.name or "v3" in f.name), json_files[0])
    with open(data_file, encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    for i, node in enumerate(nodes):
        idx2label[i] = node.get("id", str(i))

    # 2) Optional: read .dat for S (source) and D (destination) to set depot for index D
    dat_files = list(folder.glob("*.dat"))
    if dat_files:
        dat_path = dat_files[0]
        with open(dat_path, encoding="utf-8") as f:
            text = f.read()
        s_match = re.search(r"S\s*=\s*(\d+)", text)
        d_match = re.search(r"D\s*=\s*(\d+)", text)
        if s_match and d_match:
            s_idx = int(s_match.group(1))
            d_idx = int(d_match.group(1))
            # If destination index is beyond JSON nodes (e.g. 16 when we have 0..15), same as depot
            if d_idx not in idx2label and s_idx in idx2label:
                idx2label[d_idx] = idx2label[s_idx]

    return idx2label


def _is_numeric_path(line: str) -> bool:
    """True if line looks like a path of node indices (e.g. 0->1->13->16)."""
    line = line.strip()
    if not line or "->" not in line:
        return False
    # Must start with a digit and only contain digits and -> (and optional trailing ->)
    parts = [p.strip() for p in line.replace("->", " ").split()]
    return all(p.isdigit() for p in parts if p)


def convert_path(
    path_str: str,
    idx2label: dict[int, str],
    in_sep: str = "->",
    out_sep: str = " -> ",
) -> str:
    """
    Convert a numeric node path string into a labeled path using idx2label.
    Same behavior as path_con.convert_path.
    """
    raw = [seg.strip() for seg in path_str.split(in_sep)]
    raw = [seg for seg in raw if seg]

    out = []
    for seg in raw:
        if seg.isdigit():
            out.append(idx2label.get(int(seg), seg))
        else:
            out.append(seg)
    return out_sep.join(out)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    instance_folder = Path(sys.argv[1])
    try:
        idx2label = load_mapping_from_instance(instance_folder)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    paths_to_convert: list[str] = []

    if len(sys.argv) >= 3:
        if sys.argv[2] == "--file":
            if len(sys.argv) < 4:
                print("Usage: path_con_from_instance.py <instance_folder> --file <path_file>", file=sys.stderr)
                sys.exit(1)
            path_file = Path(sys.argv[3])
            if not path_file.exists():
                print(f"File not found: {path_file}", file=sys.stderr)
                sys.exit(1)
            with open(path_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and _is_numeric_path(line):
                        paths_to_convert.append(line)
        else:
            # Single path from command line
            paths_to_convert.append(sys.argv[2])
    else:
        # Read from stdin, one path per line
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                paths_to_convert.append(line)

    for path_str in paths_to_convert:
        if not _is_numeric_path(path_str):
            continue
        labeled = convert_path(path_str, idx2label)
        print(labeled)


if __name__ == "__main__":
    main()
