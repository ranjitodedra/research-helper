"""
Extract metrics from GA, CPLEX, AC (ACO), and CW output txt files into CSV files.
Processes subfolders named by node count (e.g. 8, 12, 16, 20, 24)
and writes runtime, travelTime, distance, energy_consumption,
energy_charge_CS, energy_charge_ERS.

GA runtime is taken from "Mean Per-Run Runtime:  X.XX seconds" when present;
falls back to "Runtime: X.XX seconds" for older outputs.

AC/CW use the same solution-summary lines as GA; runtime from
"Total Runtime:  X.XX seconds" in their output files.
"""

import argparse
import csv
import logging
import re
from pathlib import Path

# Regex patterns for GA output format
RE_GA_TRAVEL_TIME = re.compile(
    r"Total Travel Time:\s+[\d.]+\s+hours\s+\(([\d.]+)\s+min\)"
)
RE_GA_DISTANCE = re.compile(r"Total Distance:\s+([\d.]+)\s+km")
RE_GA_ENERGY_DEPLETION = re.compile(r"Total Energy Depletion:\s+([\d.]+)\s+kWh")
RE_GA_ENERGY_CHARGE_SC = re.compile(r"Total Energy Charged \(SC\):\s+([\d.]+)\s+kWh")
RE_GA_ENERGY_CHARGE_DWC = re.compile(r"Total Energy Charged \(DWC\):\s+([\d.]+)\s+kWh")
RE_GA_MEAN_RUNTIME = re.compile(
    r"Mean Per-Run Runtime:\s+([\d.]+)\s+seconds",
    re.IGNORECASE,
)
RE_GA_RUNTIME_LEGACY = re.compile(r"Runtime:\s+([\d.]+)\s+seconds")

# AC / CW (heuristic) — same metric lines as GA; runtime from summary block
RE_HEURISTIC_RUNTIME = re.compile(r"Total Runtime:\s+([\d.]+)\s+seconds", re.IGNORECASE)

# Regex patterns for CPLEX output format
RE_CPLEX_TRAVEL_TIME = re.compile(r"Travel time:\s+([\d.]+)")
RE_CPLEX_DISTANCE = re.compile(r"Total distance taken:\s+([\d.]+)")
RE_CPLEX_ENERGY_DEPLETION = re.compile(r"Total energy depletion:\s+([\d.]+)")
RE_CPLEX_ENERGY_CHARGE_CS = re.compile(
    r"Total energy charged at charging stations:\s+([\d.]+)"
)
RE_CPLEX_ENERGY_CHARGE_ERS = re.compile(r"Total energy charged at Eroad:\s+([\d.]+)")

RE_NODE_FOLDER = re.compile(r"^\d+$")

CSV_NAMES = (
    "runtime.csv",
    "travelTime.csv",
    "distance.csv",
    "energy_consumption.csv",
    "energy_charge_CS.csv",
    "energy_charge_ERS.csv",
)
CSV_METRIC_KEYS = (
    "runtime_sec",
    "travel_time_min",
    "distance_km",
    "energy_depletion",
    "energy_charge_CS",
    "energy_charge_DWC",
)


def _extract_ga_runtime_sec(text: str) -> str:
    """Prefer mean per-run runtime; else legacy single Runtime line."""
    m = RE_GA_MEAN_RUNTIME.search(text)
    if m:
        return m.group(1).strip()
    m = RE_GA_RUNTIME_LEGACY.search(text)
    return m.group(1).strip() if m else ""


def parse_ga_output(filepath: Path) -> dict | None:
    """
    Parse a GA output txt file and return extracted metrics.
    Returns None if file missing, empty, or unparseable.
    """
    if not filepath.exists():
        return None
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logging.warning("Could not read %s", filepath)
        return None
    if not text.strip():
        logging.warning("Empty file: %s", filepath)
        return None

    def search(pattern: re.Pattern) -> str:
        m = pattern.search(text)
        return m.group(1).strip() if m else ""

    return {
        "travel_time_min": search(RE_GA_TRAVEL_TIME),
        "distance_km": search(RE_GA_DISTANCE),
        "energy_depletion": search(RE_GA_ENERGY_DEPLETION),
        "energy_charge_CS": search(RE_GA_ENERGY_CHARGE_SC),
        "energy_charge_DWC": search(RE_GA_ENERGY_CHARGE_DWC),
        "runtime_sec": _extract_ga_runtime_sec(text),
    }


def parse_ac_cw_output(filepath: Path) -> dict | None:
    """
    Parse AC (ant colony) or CW (Clarke–Wright) output.
    Same summary fields as GA; runtime from 'Total Runtime: X.XX seconds'.
    """
    if not filepath.exists():
        return None
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logging.warning("Could not read %s", filepath)
        return None
    if not text.strip():
        logging.warning("Empty file: %s", filepath)
        return None

    def search(pattern: re.Pattern) -> str:
        m = pattern.search(text)
        return m.group(1).strip() if m else ""

    m_rt = RE_HEURISTIC_RUNTIME.search(text)
    runtime_sec = m_rt.group(1).strip() if m_rt else ""

    return {
        "travel_time_min": search(RE_GA_TRAVEL_TIME),
        "distance_km": search(RE_GA_DISTANCE),
        "energy_depletion": search(RE_GA_ENERGY_DEPLETION),
        "energy_charge_CS": search(RE_GA_ENERGY_CHARGE_SC),
        "energy_charge_DWC": search(RE_GA_ENERGY_CHARGE_DWC),
        "runtime_sec": runtime_sec,
    }


def parse_cplex_output(filepath: Path) -> dict | None:
    """
    Parse a CPLEX output txt file and return extracted metrics.
    CPLEX uses "Travel time" in minutes; no runtime in file.
    energy_charge_DWC maps to "Total energy charged at Eroad".
    """
    if not filepath.exists():
        return None
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logging.warning("Could not read %s", filepath)
        return None
    if not text.strip():
        logging.warning("Empty file: %s", filepath)
        return None

    def search(pattern: re.Pattern) -> str:
        m = pattern.search(text)
        return m.group(1).strip() if m else ""

    return {
        "travel_time_min": search(RE_CPLEX_TRAVEL_TIME),
        "distance_km": search(RE_CPLEX_DISTANCE),
        "energy_depletion": search(RE_CPLEX_ENERGY_DEPLETION),
        "energy_charge_CS": search(RE_CPLEX_ENERGY_CHARGE_CS),
        "energy_charge_DWC": search(RE_CPLEX_ENERGY_CHARGE_ERS),
        "runtime_sec": "",
    }


def discover_node_folders(base_dir: Path) -> list[tuple[str, Path]]:
    """
    Find subdirs whose names are integer node counts (e.g. 8, 12, 16, 20, 24)
    and return (node_label, path) sorted numerically.
    Fallback: any directory containing GA_output.txt.
    """
    pairs: list[tuple[str, Path]] = []
    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        if RE_NODE_FOLDER.match(p.name):
            pairs.append((p.name, p))

    if pairs:
        pairs.sort(key=lambda item: int(item[0]))
        return pairs

    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        if (p / "GA_output.txt").exists():
            pairs.append((p.name, p))
    pairs.sort(key=lambda x: x[0])
    return pairs


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description=(
            "Extract metrics from GA/CPLEX output txt files to CSV "
            "(node-count subfolders, e.g. 8, 12, 16)."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Root directory containing numeric node subfolders (default: script dir)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write CSV files (default: same as input-dir)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    input_dir = args.input_dir or script_dir
    output_dir = args.output_dir or input_dir

    if not input_dir.is_dir():
        logging.error("Input directory does not exist: %s", input_dir)
        return

    pairs = discover_node_folders(input_dir)
    if not pairs:
        logging.warning(
            "No node subfolders (numeric names or with GA_output.txt) found in %s",
            input_dir,
        )
        return

    rows_by_metric: list[list[dict]] = [[] for _ in CSV_METRIC_KEYS]

    for node_label, folder in pairs:
        row_ga = parse_ga_output(folder / "GA_output.txt")
        row_cplex = parse_cplex_output(folder / "CPLEX_output.txt")
        row_ac = parse_ac_cw_output(folder / "AC_output.txt")
        row_cw = parse_ac_cw_output(folder / "CW_output.txt")

        for i, key in enumerate(CSV_METRIC_KEYS):
            r = {"node": node_label}
            r["GA"] = (row_ga or {}).get(key, "")
            r["CPLEX"] = (row_cplex or {}).get(key, "")
            r["AC"] = (row_ac or {}).get(key, "")
            r["CW"] = (row_cw or {}).get(key, "")
            rows_by_metric[i].append(r)

    fieldnames = ["node", "GA", "CPLEX", "AC", "CW"]
    for csv_name, rows in zip(CSV_NAMES, rows_by_metric):
        out_path = output_dir / csv_name
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        logging.info("Wrote %s", out_path)


if __name__ == "__main__":
    main()
